#include <scale_factors.h>

namespace common {

template <> void Matrix<1>::init() { storage[0][0] = 1; }

template <> void Matrix<2>::init() {
    storage = {};
    storage[0][0] = 1;
    storage[1][1] = 1;
}

template <> void Matrix<3>::init() {
    storage = {};
    storage[0][0] = 1;
    storage[1][1] = 1;
    storage[2][2] = 1;
}

template <> void Matrix<4>::init() {
    storage = {};
    storage[0][0] = 1;
    storage[1][1] = 1;
    storage[2][2] = 1;
    storage[3][3] = 1;
}

#ifndef NO_SPECIALIZE_FOR_SIMPLE_CASE
// Specialization for simple cases
template <>
float combineScaleFactors<1>(const std::array<ScaleFactor, 1> &sfs,
                             const Matrix<1> &correlations, Variation variation) {
    return sfs[0].first + static_cast<int>(variation) * sfs[0].second;
}

template <>
float combineScaleFactors<2>(const std::array<ScaleFactor, 2> &sfs,
                             const Matrix<2> &correlations, Variation variation) {

    float sf_nominal = sfs[0].first * sfs[1].first;
    if (variation == Variation::NOMINAL)
        return sf_nominal;

    float sf_uncertainty =
        std::sqrt((sfs[0].second * sfs[0].second) / (sfs[0].first * sfs[0].first) +
                  (sfs[1].second * sfs[1].second) / (sfs[1].first * sfs[1].first) +
                  2 * correlations(0, 1) * (sfs[0].second * sfs[1].second) /
                      (sfs[0].first * sfs[1].first));

    return sf_nominal * (1 + static_cast<int>(variation) * sf_uncertainty);
}
#endif
}
