#pragma once

#include <array>
#include <cmath>
#include <initializer_list>
#include <stdexcept>
#include <vector>

namespace common {

/**
 * A lightweight squared-matrix class
 */
template <std::size_t N> struct Matrix {
    using col_type = std::array<float, N>;

  public:
    Matrix() { init(); }

    Matrix(std::initializer_list<col_type> init) {
        if (init.size() != N)
            throw std::runtime_error("Invalid data");

        std::size_t index = 0;
        for (const auto &v : init) {
            if (v.size() != N) {
                throw std::runtime_error("Non-square matrix");
            }
            storage[index++] = v;
        }
    }

    float operator()(std::size_t row, std::size_t col) const { return storage[row][col]; }

    std::size_t rows() const { return N; }
    std::size_t cols() const { return N; }

  private:
    void init() {
        // Default implementation
        storage = {};
        for (std::size_t i = 0; i < N; i++)
            storage[i][i] = 1;
    }

    std::array<std::array<float, N>, N> storage;
};

static const Matrix<1> IDENTITY_1x1;
static const Matrix<2> IDENTITY_2x2;
static const Matrix<3> IDENTITY_3x3;
static const Matrix<4> IDENTITY_4x4;

enum class Variation { NOMINAL = 0, UP = 1, DOWN = -1 };

using ScaleFactor = std::pair<float, float>;

/**
  Compute the combined value and the corresponding uncertainty on a product of N
scale-factors, taking into account possible correlations between the parameters.

  @param sfs An array of ScaleFactor. A scale-factor is defined by a pair of number, the
 first is the nominal value, and the second the uncertainty of this value
  @param correlations The correlations matrix of the scale-factors
  @param variation The type of variation requested.
**/
template <std::size_t N>
float combineScaleFactors(const std::array<ScaleFactor, N> &sfs,
                          const Matrix<N> &correlations, Variation variation) {

    float sf_nominal = 1;
    float sf_uncertainty = 0;

    for (size_t i = 0; i < N; i++) {

        // Product of all scale factors
        sf_nominal *= sfs[i].first;

        for (size_t j = 0; j < N; j++) {

            sf_uncertainty += 1. / (sfs[i].first * sfs[j].first) * correlations(i, j) *
                              sfs[i].second * sfs[j].second;
        }
    }

    sf_uncertainty = sf_nominal * std::sqrt(sf_uncertainty);

    return sf_nominal + static_cast<int>(variation) * sf_uncertainty;
}

/**
  Compute the combined value and the corresponding uncertainty on a product of N
scale-factors, concidering that all the parameters are non-correlated.

  @param sfs An array of ScaleFactor. A scale-factor is defined by a pair of number, the
 first is the nominal value, and the second the uncertainty of this value
  @param variation The type of variation requested.
**/
template <std::size_t N>
float combineScaleFactors(const std::array<ScaleFactor, N> &sfs, Variation variation) {
    static Matrix<N> identity_matrix;
    return combineScaleFactors(sfs, identity_matrix, variation);
}
}
