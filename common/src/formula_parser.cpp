#include <formula_parser.h>

namespace parser
{
    bool parser::parse(const std::string& line, std::set<std::string>& identifiers) {
        m_grammar.set_identifiers(identifiers);

        bool result = qi::phrase_parse(
                line.begin(),
                line.end(),
                m_grammar,
                ascii::space);

        return result;
    }
}
