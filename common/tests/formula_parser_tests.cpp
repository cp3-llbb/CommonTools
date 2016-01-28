#include "catch.hpp"

#include <formula_parser.h>

TEST_CASE("Formula parser", "[parser]") {

    namespace qi = boost::spirit::qi;
    namespace ascii = boost::spirit::ascii;

    parser::grammar<std::string::const_iterator> grammar;

    auto parse = [&grammar](const std::string& line) {
        auto begin = line.cbegin();
        auto end = line.cend();

        bool ret = qi::phrase_parse(
                begin,
                end,
                grammar,
                ascii::space);

        return ret && (begin == end);
    };

    std::string line = "a + b";
    REQUIRE(parse(line));

    std::set<std::string> expressions;
    grammar.set_identifiers(expressions);
    line = "expression->function(value1, value2) * ((a > b) ? 5 : ((sqrt(24 ^ 4 % 14) < array[index]) ? 1 : 8))";
    REQUIRE(parse(line));
    REQUIRE(expressions.size() == 9);

    expressions.clear();
    line = "12 * function({{{number1, error1}, {number2, error2}}}, {{1, correlation}, {correlation, 1}}, common::Variation::NOMINAL)";
    REQUIRE(parse(line));
    REQUIRE(expressions.size() == 9);

    expressions.clear();
    line = "parsing( * branch1 + branch2 * branch3";
    REQUIRE(!parse(line));
}
