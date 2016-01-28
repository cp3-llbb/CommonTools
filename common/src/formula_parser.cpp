#include <formula_parser.h>

namespace parser
{
    bool parser::parse(const std::string& line, std::set<std::string>& identifiers) {
        m_grammar.set_identifiers(identifiers);

        auto begin = line.begin();
        auto end = line.end();

        bool result = qi::phrase_parse(
                begin,
                end,
                m_grammar,
                ascii::space);

        return result && (begin == end);
    }
}
