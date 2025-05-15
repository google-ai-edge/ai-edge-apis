lexer grammar AntlrJsonLexer;

// Structural Characters
OPEN_BRACE : '{';
CLOSE_BRACE : '}';
OPEN_BRACKET : '[';
CLOSE_BRACKET : ']';
COMMA : ',';
COLON : ':';

// Literals
BOOLEAN : 'true' | 'false';
NONE : 'null';

// Literals function name key
FUNCTION_NAME: '"' 'name' '"' ;

// Literals arguments key
FUNCTION_ARGUMENTS: '"' ( 'args' | 'arguments' ) '"' ;

// String: Double-quoted with escape sequences
STRING : '"' ( ESC | ~["\\] )* '"';

fragment ESC : '\\' ( ["\\/bfnrt] | UNICODE );
fragment UNICODE : 'u' HEX HEX HEX HEX;
fragment HEX : [0-9a-fA-F];

// Number: Integer and floating-point, including exponents
NUMBER : '-'? INT ( FRAC | EXP )? | '-'? FRAC | '-'? EXP ;

fragment INT : '0' | [1-9] [0-9]*;
fragment FRAC : '.' [0-9]+;
fragment EXP : [eE] [+-]? [0-9]+;

// Whitespace: Skipped
WS : [ \t\n\r]+ -> skip;
