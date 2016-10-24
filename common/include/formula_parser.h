#pragma once

#include <boost/config/warning_disable.hpp>
#include <boost/spirit/include/qi.hpp>
#include <boost/spirit/include/phoenix.hpp>

#include <string>
#include <set>

namespace parser
{
    namespace qi = boost::spirit::qi;
    namespace phoenix = boost::phoenix;
    namespace ascii = boost::spirit::ascii;

    template<typename Iterator>
    struct grammar: qi::grammar<Iterator, ascii::space_type> {

        public:
            grammar(): grammar::base_type(translation_unit),
                ELLIPSIS("..."), RIGHT_ASSIGN(">>="), LEFT_ASSIGN("<<="),
                ADD_ASSIGN("+="), SUB_ASSIGN("-="), MUL_ASSIGN("*="),
                DIV_ASSIGN("/="), MOD_ASSIGN("%="), AND_ASSIGN("&="),
                XOR_ASSIGN("^="), OR_ASSIGN("|="), RIGHT_OP(">>"), LEFT_OP("<<"),
                INC_OP("++"), DEC_OP("--"), PTR_OP("->"), AND_OP("&&"),
                OR_OP("||"), LE_OP("<="), GE_OP(">="), EQ_OP("=="), NE_OP("!="),
                NAMESPACE("::"),
                SEMICOLON(';'),
                COMMA(','), COLON(':'), ASSIGN('='), LEFT_PAREN('('),
                RIGHT_PAREN(')'), DOT('.'), ADDROF('&'), BANG('!'), TILDE('~'),
                MINUS('-'), PLUS('+'), STAR('*'), SLASH('/'), PERCENT('%'),
                LT_OP('<'), GT_OP('>'), XOR('^'), OR('|'), QUEST('?')
            {

                keywords =
                    "auto", "break", "case", "char", "const", "continue", "default",
                    "do", "double", "else", "enum", "extern", "float", "for",
                    "goto", "if", "int", "long", "register", "return", "short",
                    "signed", "sizeof", "static", "struct", "switch", "typedef",
                    "union", "unsigned", "void", "volatile", "while";

                LEFT_BRACE = qi::lit('{') | qi::lit("<%");
                RIGHT_BRACE = qi::lit('}') | qi::lit("%>");
                LEFT_BRACKET = qi::lit('[') | qi::lit("<:");
                RIGHT_BRACKET = qi::lit(']') | qi::lit(":>");

                CHAR =       qi::lit("char");
                CONST =      qi::lit("const");
                DOUBLE =     qi::lit("double");
                FLOAT =      qi::lit("float");
                INT =        qi::lit("int");
                LONG =       qi::lit("long");
                SHORT =      qi::lit("short");
                SIGNED =     qi::lit("signed");
                VOID =       qi::lit("void");
                VOLATILE =   qi::lit("volatile");

                using qi::eps;
                using qi::double_;
                using qi::float_;
                using qi::int_;
                using ascii::char_;
                using ascii::alpha;
                using ascii::alnum;
                using qi::lexeme;
                using phoenix::push_back;

                IDENTIFIER = qi::as_string[((alpha | char_('_') | char_('$')) >> *(alnum | char_('_') | char_('$')))
                - (keywords >> (char_ - (alnum | '_' | '$')))
                ][phoenix::bind(&grammar<Iterator>::new_id, this, qi::_1)];

                QUOTED_STRING %= lexeme['"' >> +(char_ - '"') >> '"'];

                primary_expression
                    = IDENTIFIER
                    | double_
                    | float_
                    | int_
                    | QUOTED_STRING
                    | LEFT_PAREN >> expression >> RIGHT_PAREN
                    | LEFT_BRACE >> expression >> RIGHT_BRACE
                    ;


                postfix_expression
                    = primary_expression >> postfix_expression_helper
                    ;

                postfix_expression_helper
                    =   (
                            LEFT_BRACKET >> expression >> RIGHT_BRACKET
                        |   LEFT_PAREN >> -argument_expression_list >> RIGHT_PAREN
                        |   LEFT_BRACE >> expression >> RIGHT_BRACE
                        |   DOT >> IDENTIFIER
                        |   PTR_OP >> IDENTIFIER
                        |   NAMESPACE >> IDENTIFIER
                        ) >>
                        postfix_expression_helper
                    | eps
                    ;

                argument_expression_list
                    = assignment_expression >> *(COMMA >> assignment_expression)
                    ;

                unary_expression
                    = postfix_expression
                    | INC_OP >> unary_expression
                    | DEC_OP >> unary_expression
                    | unary_operator >> cast_expression
                    ;

                unary_operator
                    = qi::lit(ADDROF)
                    | STAR
                    | PLUS
                    | MINUS
                    | TILDE
                    | BANG
                    ;

                cast_expression
                    = LEFT_PAREN >> type_name >> RIGHT_PAREN >> cast_expression
                    | unary_expression
                    ;

                multiplicative_expression
                    = cast_expression >> multiplicative_expression_helper
                    ;

                multiplicative_expression_helper
                    =   (
                            STAR >> cast_expression
                        |   SLASH >> cast_expression
                        |   PERCENT >> cast_expression
                        ) >>
                        multiplicative_expression_helper
                    | eps
                    ;

                additive_expression
                    = multiplicative_expression >> additive_expression_helper
                    ;

                additive_expression_helper
                    =   (
                            PLUS >> multiplicative_expression
                        |   MINUS >> multiplicative_expression
                        ) >>
                        additive_expression_helper
                    | eps
                    ;

                shift_expression
                    = additive_expression >> shift_expression_helper
                    ;

                shift_expression_helper
                    =   (
                            LEFT_OP >> additive_expression
                        |   RIGHT_OP >> additive_expression
                        ) >>
                        shift_expression_helper
                    | eps
                    ;

                relational_expression
                    = shift_expression >> relational_expression_helper
                    ;

                relational_expression_helper
                    =   (
                            LT_OP >> shift_expression
                        |   GT_OP >> shift_expression
                        |   LE_OP >> shift_expression
                        |   GE_OP >> shift_expression
                        ) >>
                        relational_expression_helper
                    | eps
                    ;

                equality_expression
                    = relational_expression >> equality_expression_helper
                    ;

                equality_expression_helper
                    =   (
                            EQ_OP >> relational_expression
                        |   NE_OP >> relational_expression
                        ) >>
                        equality_expression_helper
                    | eps
                    ;

                and_expression
                    = equality_expression >> and_expression_helper
                    ;

                and_expression_helper
                    = ADDROF >> equality_expression >> and_expression_helper
                    | eps
                    ;

                exclusive_or_expression
                    = and_expression >> exclusive_or_expression_helper
                    ;

                exclusive_or_expression_helper
                    = XOR >> and_expression >> exclusive_or_expression_helper
                    | eps
                    ;

                inclusive_or_expression
                    = exclusive_or_expression >> inclusive_or_expression_helper
                    ;

                inclusive_or_expression_helper
                    = OR >> exclusive_or_expression >> inclusive_or_expression_helper
                    | eps
                    ;

                logical_and_expression
                    = inclusive_or_expression >> logical_and_expression_helper
                    ;

                logical_and_expression_helper
                    = AND_OP >> inclusive_or_expression >> logical_and_expression_helper
                    | eps
                    ;

                logical_or_expression
                    = logical_and_expression >> logical_or_expression_helper
                    ;

                logical_or_expression_helper
                    = OR_OP >> logical_and_expression >> logical_or_expression_helper
                    | eps
                    ;

                conditional_expression
                    = logical_or_expression >> conditional_expression_helper
                    ;

                conditional_expression_helper
                    = QUEST >> expression >> COLON
                        >> conditional_expression >> conditional_expression_helper
                    | eps
                    ;

                assignment_expression
                    = conditional_expression.alias()
                    ;

                expression
                    = assignment_expression >> expression_helper
                    ;

                expression_helper
                    = COMMA >> assignment_expression >> expression_helper
                    | eps
                    ;

                constant_expression
                    = conditional_expression
                    ;

                type_specifier
                    = VOID
                    | CHAR
                    | SHORT
                    | INT
                    | LONG
                    | FLOAT
                    | DOUBLE
                    | SIGNED
                    | UNSIGNED
                    ;

                specifier_qualifier_list
                    =   (
                            type_specifier
                        |   type_qualifier
                        ) >>
                        -specifier_qualifier_list
                    ;

                type_qualifier
                    = CONST
                    | VOLATILE
                    ;

                pointer
                    = STAR >> -(type_qualifier_list || pointer)
                    ;

                type_qualifier_list
                    = +type_qualifier
                    ;

                identifier_list
                    = IDENTIFIER >> *(COMMA >> IDENTIFIER)
                    ;

                type_name
                    = specifier_qualifier_list >> -abstract_declarator
                    ;

            // parser start symbol
                translation_unit
                    = expression.alias()
                    ;
            }

            void new_id(const std::string& id) {
                if (m_identifiers)
                    m_identifiers->emplace(id);
            }

            void set_identifiers(std::set<std::string>& ids) {
                m_identifiers = &ids;
            }

        private:
            qi::rule<Iterator, ascii::space_type> IDENTIFIER;
            qi::rule<Iterator, ascii::space_type> QUOTED_STRING;

            qi::rule<Iterator, ascii::space_type> parameter;
            qi::rule<Iterator, ascii::space_type> function_call;

            // Operators
            std::string
                    ELLIPSIS, RIGHT_ASSIGN, LEFT_ASSIGN, ADD_ASSIGN, SUB_ASSIGN,
                    MUL_ASSIGN, DIV_ASSIGN, MOD_ASSIGN, AND_ASSIGN, XOR_ASSIGN,
                    OR_ASSIGN, RIGHT_OP, LEFT_OP, INC_OP, DEC_OP, PTR_OP, AND_OP,
                    OR_OP, LE_OP, GE_OP, EQ_OP, NE_OP, NAMESPACE;

            char
                    SEMICOLON, COMMA, COLON, ASSIGN, LEFT_PAREN, RIGHT_PAREN,
                    DOT, ADDROF, BANG, TILDE, MINUS, PLUS, STAR, SLASH, PERCENT,
                    LT_OP, GT_OP, XOR, OR, QUEST;

            qi::symbols<> keywords;

            qi::rule<Iterator, ascii::space_type>
                    LEFT_BRACE, RIGHT_BRACE, LEFT_BRACKET, RIGHT_BRACKET;

            qi::rule<Iterator, ascii::space_type>
                    CHAR, CONST, DOUBLE, FLOAT, INT, LONG, SHORT, SIGNED, SIZEOF, UNSIGNED, VOID, VOLATILE;

            qi::rule<Iterator, ascii::space_type>
                    primary_expression, postfix_expression, postfix_expression_helper,
                    argument_expression_list, unary_expression, unary_operator,
                    cast_expression,
                    multiplicative_expression, multiplicative_expression_helper,
                    additive_expression, additive_expression_helper,
                    shift_expression, shift_expression_helper,
                    relational_expression, relational_expression_helper,
                    equality_expression, equality_expression_helper,
                    and_expression, and_expression_helper,
                    exclusive_or_expression, exclusive_or_expression_helper,
                    inclusive_or_expression, inclusive_or_expression_helper,
                    logical_and_expression, logical_and_expression_helper,
                    logical_or_expression, logical_or_expression_helper,
                    conditional_expression, conditional_expression_helper,
                    assignment_expression, assignment_operator,
                    expression, expression_helper, constant_expression, declaration,
                    declaration_specifiers, init_declarator_list, init_declarator,
                    type_specifier, specifier_qualifier_list, type_qualifier, declarator,
                    pointer, type_qualifier_list, identifier_list, type_name,
                    abstract_declarator,
                    direct_abstract_declarator, direct_abstract_declarator_helper,
                    statement;

            qi::rule<Iterator, ascii::space_type>
                    translation_unit;

            std::set<std::string>* m_identifiers = nullptr;
    };

    class parser {
        public:
            bool parse(const std::string& line, std::set<std::string>& identifiers);

        private:
            grammar<std::string::const_iterator> m_grammar;
    };
}
