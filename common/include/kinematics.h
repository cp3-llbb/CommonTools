#pragma once

#include <Math/LorentzVector.h>

namespace Kinematics {
  using LorentzVector = ROOT::Math::LorentzVector<ROOT::Math::PtEtaPhiE4D<float> >;

  float deltaPhi( const LorentzVector& pa, const LorentzVector& pb )
  {
    return std::acos(std::min<float>(std::max<float>(-1.,
            (pa.Px()*pb.Px()+pa.Py()*pb.Py())/(pa.Pt()*pb.Pt())
           ), 1.));
  }
  float deltaR( const LorentzVector& pa, const LorentzVector& pb )
  {
    return std::sqrt(std::pow(pb.Eta()-pa.Eta(), 2)+std::pow(deltaPhi(pa, pb), 2));
  }

  float signedDeltaPhi( const LorentzVector& pa, const LorentzVector& pb )
  {
    return ( ( pb.Py()*pa.Px()-pb.Px()*pa.Py() > 0. ) ? 1. : -1. )*deltaPhi(pa, pb);
  }

  float signedDeltaEta( const LorentzVector& pa, const LorentzVector& pb )
  {
    const float etaA{pa.Eta()};
    const float etaB{pb.Eta()};
    return ( etaA > 0. ? 1. : -1. )*( etaB - etaA ); // (small) positive and negative = more and less forward
  }
};
