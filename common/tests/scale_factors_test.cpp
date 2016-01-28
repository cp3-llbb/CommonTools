#include "catch.hpp"

#include <scale_factors.h>

#include <cmath>

template<std::size_t N>
bool is_identity(const common::Matrix<N>& matrix) {
    for (std::size_t i = 0; i < N; i++) {
        for (std::size_t j = 0; j < N; j++) {
            if (!(matrix(i, j) == ((i == j) ? 1 : 0)))
                return false;
        }
    }

    return true;
}

TEST_CASE("Matrix", "[matrix]") {

    INFO("2x2 identity matrix");
    auto matrix = common::Matrix<2>();
    REQUIRE(is_identity(matrix));

    INFO("10x10 identity matrix");
    REQUIRE(is_identity(common::Matrix<10>()));

    INFO("Empty matrix");
    auto empty_matrix = common::Matrix<2>({{0, 0}, {0, 0}});
    REQUIRE(empty_matrix(0, 0) == 0);
    REQUIRE(empty_matrix(1, 1) == 0);
    REQUIRE(empty_matrix(0, 1) == 0);
    REQUIRE(empty_matrix(1, 0) == 0);

    INFO("Off-diagonal matrix");
    auto weird_matrix = common::Matrix<2>({{0, 1}, {1, 0}});
    REQUIRE(weird_matrix(0, 0) == 0);
    REQUIRE(weird_matrix(1, 1) == 0);
    REQUIRE(weird_matrix(0, 1) == 1);
    REQUIRE(weird_matrix(1, 0) == 1);

    REQUIRE(is_identity(common::IDENTITY_1x1));
    REQUIRE(is_identity(common::IDENTITY_2x2));
    REQUIRE(is_identity(common::IDENTITY_3x3));
    REQUIRE(is_identity(common::IDENTITY_4x4));
}

TEST_CASE("Scale-factors combinations", "[sf]") {
    REQUIRE(common::combineScaleFactors<1>({{{1, 1}}}, {{1}}, common::Variation::NOMINAL) == 1);
    REQUIRE(common::combineScaleFactors<1>({{{1, 1}}}, {{1}}, common::Variation::UP) == 2);
    REQUIRE(common::combineScaleFactors<1>({{{1, 1}}}, {{1}}, common::Variation::DOWN) == 0);

    float a = 0.75;
    float a_error = 0.5;
    float b = 1;
    float b_error = 0.2;

    float combined_sf = a * b;
    float sf_uncertainty = combined_sf * std::sqrt((a_error * a_error) / (a * a) + (b_error * b_error) / (b * b));

    REQUIRE(common::combineScaleFactors<2>({{{a, a_error}, {b, b_error}}}, common::Variation::NOMINAL) == Approx(combined_sf));
    REQUIRE(common::combineScaleFactors<2>({{{a, a_error}, {b, b_error}}}, common::Variation::UP) == Approx((combined_sf + sf_uncertainty)));
    REQUIRE(common::combineScaleFactors<2>({{{a, a_error}, {b, b_error}}}, common::Variation::DOWN) == Approx((combined_sf - sf_uncertainty)));

    sf_uncertainty = combined_sf * std::sqrt((a_error * a_error) / (a * a) + (b_error * b_error) / (b * b) + 2 * (a_error * b_error) / (a * b));
    common::Matrix<2> correlation = {{1, 1}, {1, 1}};

    REQUIRE(common::combineScaleFactors<2>({{{a, a_error}, {b, b_error}}}, correlation, common::Variation::NOMINAL) == Approx(combined_sf));
    REQUIRE(common::combineScaleFactors<2>({{{a, a_error}, {b, b_error}}}, correlation, common::Variation::UP) == Approx(combined_sf + sf_uncertainty));
    REQUIRE(common::combineScaleFactors<2>({{{a, a_error}, {b, b_error}}}, correlation, common::Variation::DOWN) == Approx(combined_sf - sf_uncertainty));

}
