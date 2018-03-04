#pragma once

#include "BinnedValuesJSONParser.h"
#include <stdexcept>

class ILeptonScaleFactor {
public:
  virtual ~ILeptonScaleFactor() {}
  virtual float get(const Parameters& parameters, Variation variation) const = 0;
};
class IDiLeptonScaleFactor {
public:
  virtual ~IDiLeptonScaleFactor() {}
  virtual float get(const Parameters& l1Param, const Parameters& l2Param, Variation variation) const = 0;
};

class IJetScaleFactor {
public:
  virtual ~IJetScaleFactor() {}

  enum Flavour {
    Light  = 0,
    Charm  = 1,
    Beauty = 2
  };
  static inline Flavour get_flavour(int hadron_flavour) {
    switch(hadron_flavour) {
      case 5:
        return Flavour::Beauty;
      case 4:
        return Flavour::Charm;
      default:
        return Flavour::Light;
    }
  }
  virtual float get(const Parameters& parameters, Flavour flavour, Variation variation) const = 0;
};

/**
 * Simple case: one scale factor from file
 */
class ScaleFactor : public ILeptonScaleFactor {
public:
  explicit ScaleFactor(const std::string& file)
  : m_values{BinnedValuesJSONParser(file).get_values()}
  {}
  virtual ~ScaleFactor() {}

  virtual float get(const Parameters& parameters, Variation variation) const override final {
    return m_values.get(parameters)[static_cast<std::size_t>(variation)];
  }
private:
  BinnedValues m_values;
};

/**
 * Dilepton scalefactor from two lepton scalefactors (takes a parameter set for each)
 */
class DiLeptonFromLegsScaleFactor : public IDiLeptonScaleFactor {
public:
  DiLeptonFromLegsScaleFactor( std::unique_ptr<ILeptonScaleFactor>&& l1_leg1
                             , std::unique_ptr<ILeptonScaleFactor>&& l1_leg2
                             , std::unique_ptr<ILeptonScaleFactor>&& l2_leg1
                             , std::unique_ptr<ILeptonScaleFactor>&& l2_leg2 )
  : m_l1_leg1{std::move(l1_leg1)}
  , m_l1_leg2{std::move(l1_leg2)}
  , m_l2_leg1{std::move(l2_leg1)}
  , m_l2_leg2{std::move(l2_leg2)}
  {}
  virtual ~DiLeptonFromLegsScaleFactor() {}

  virtual float get(const Parameters& l1Param, const Parameters& l2Param, Variation variation) const override final {
    const float eff_lep1_leg1 = m_l1_leg1->get(l1Param, variation);
    const float eff_lep1_leg2 = m_l1_leg2->get(l1Param, variation);
    const float eff_lep2_leg1 = m_l2_leg1->get(l2Param, variation);
    const float eff_lep2_leg2 = m_l2_leg2->get(l2Param, variation);

    if ( variation == Nominal ) {
      return -(eff_lep1_leg1 * eff_lep2_leg1) +
          (1 - (1 - eff_lep1_leg2)) * eff_lep2_leg1 +
          eff_lep1_leg1 * (1 - (1 - eff_lep2_leg2)) ;
    } else {
      const float nom_eff_lep1_leg1 = m_l1_leg1->get(l1Param, Nominal);
      const float nom_eff_lep1_leg2 = m_l1_leg2->get(l1Param, Nominal);
      const float nom_eff_lep2_leg1 = m_l2_leg1->get(l2Param, Nominal);
      const float nom_eff_lep2_leg2 = m_l2_leg2->get(l2Param, Nominal);

      const float nominal = -(eff_lep1_leg1 * eff_lep2_leg1) +
          (1 - (1 - eff_lep1_leg2)) * eff_lep2_leg1 +
          eff_lep1_leg1 * (1 - (1 - eff_lep2_leg2)) ;

      const float error_squared =
          std::pow(1 - nom_eff_lep2_leg1 - (1 - nom_eff_lep2_leg2), 2) *
          std::pow(eff_lep1_leg1, 2) +
          std::pow(nom_eff_lep2_leg1, 2) *
          std::pow(eff_lep1_leg2, 2) +
          std::pow(1 - nom_eff_lep1_leg1 - (1 - nom_eff_lep1_leg2), 2) *
          std::pow(eff_lep2_leg1, 2) +
          std::pow(nom_eff_lep1_leg1, 2) *
          std::pow(eff_lep2_leg2, 2);

      if ( variation == Up ) {
        return std::min(nominal+std::sqrt(error_squared), 1.f);
      } else if ( variation == Down ) {
        return std::max(0.f, nominal-std::sqrt(error_squared));
      }
    }
  }
private:
  std::unique_ptr<ILeptonScaleFactor> m_l1_leg1;
  std::unique_ptr<ILeptonScaleFactor> m_l1_leg2;
  std::unique_ptr<ILeptonScaleFactor> m_l2_leg1;
  std::unique_ptr<ILeptonScaleFactor> m_l2_leg2;
};

/**
 * B-tagging scale factor (depends on flavour)
 */
class BTaggingScaleFactor : public IJetScaleFactor {
public:
  BTaggingScaleFactor(const std::string& lightFile, const std::string& charmFile, const std::string& beautyFile)
  : m_lightValues {BinnedValuesJSONParser(lightFile ).get_values()}
  , m_charmValues {BinnedValuesJSONParser(charmFile ).get_values()}
  , m_beautyValues{BinnedValuesJSONParser(beautyFile).get_values()}
  {}
  virtual ~BTaggingScaleFactor() {}

  virtual float get(const Parameters& parameters, Flavour flavour, Variation variation) const override final {
    switch(flavour) {
      case Flavour::Beauty:
        return m_beautyValues.get(parameters)[static_cast<std::size_t>(variation)];
      case Flavour::Charm:
        return m_charmValues .get(parameters)[static_cast<std::size_t>(variation)];
      case Flavour::Light:
        return m_lightValues .get(parameters)[static_cast<std::size_t>(variation)];
      default:
        throw std::invalid_argument("Unsupported flavour: "+flavour);
    }
  }
private:
  BinnedValues m_lightValues;
  BinnedValues m_charmValues;
  BinnedValues m_beautyValues;
};

#include <vector>
#include <algorithm>
#include "IndexRangeIterator.h"
/**
 * Weight between different scale factors
 */
template<class ISingle,typename... Args>
class WeightedScaleFactor : public ISingle {
public:
  WeightedScaleFactor( const std::vector<float>& probs, std::vector<std::unique_ptr<ISingle>>&& sfs )
  : m_terms{std::move(sfs)}
  {
    const double norm{1./std::accumulate(std::begin(probs), std::end(probs), 0.)};
    std::transform(std::begin(probs), std::end(probs), std::back_inserter(m_probs), [norm] ( float p ) -> float { return norm*p; } );
  }
  virtual ~WeightedScaleFactor() {}

  virtual float get(Args&&... args, Variation variation) const override final {
    return std::accumulate(IndexRangeIterator<std::size_t>(0, m_terms.size()), IndexRangeIterator<std::size_t>(m_terms.size(), m_terms.size()), 0.,
        [this,&args...,variation] ( float wsum, std::size_t i ) -> float {
          return wsum + m_probs[i]*m_terms[i]->get(std::forward<Args>(args)..., variation);
        }
      );
  }
private:
  std::vector<float> m_probs;
  std::vector<std::unique_ptr<ISingle>> m_terms;
};
using WScaleFactor         = WeightedScaleFactor<ILeptonScaleFactor,const Parameters&>;
using WLLScaleFactor       = WeightedScaleFactor<IDiLeptonScaleFactor,const Parameters&,const Parameters&>;
using WBTaggingScaleFactor = WeightedScaleFactor<IJetScaleFactor,const Parameters&,IJetScaleFactor::Flavour>;

#include <random>
/**
 * Sample according to fractions from different scale factors
 */
template<class ISingle,typename... Args>
class SampledScaleFactor : public ISingle
{
public:
  SampledScaleFactor( const std::vector<float> probs, std::vector<std::unique_ptr<ISingle>>&& sfs )
  : m_rg{42}
  , m_probs{std::discrete_distribution<std::size_t>(std::begin(probs), std::end(probs))}
  , m_terms{std::move(sfs)}
  {}
  virtual ~SampledScaleFactor() {}

  virtual float get(Args... args, Variation variation) const override final {
    return m_terms[m_probs(m_rg)]->get(std::forward<Args>(args)..., variation);
  }
private:
  mutable std::mt19937 m_rg;
  mutable std::discrete_distribution<std::size_t> m_probs;
  std::vector<std::unique_ptr<ISingle>> m_terms;
};
using SmpScaleFactor         = SampledScaleFactor<ILeptonScaleFactor,const Parameters&>;
using SmpLLScaleFactor       = SampledScaleFactor<IDiLeptonScaleFactor,const Parameters&,const Parameters&>;
using SmpBTaggingScaleFactor = SampledScaleFactor<IJetScaleFactor,const Parameters&,IJetScaleFactor::Flavour>;
