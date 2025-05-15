lexer grammar AntlrPythonLexer;

EQ: '=';
COLON: ':';
SEP: ',';
OPEN_PAR: '(';
CLOSE_PAR: ')';
OPEN_BRACE: '{';
CLOSE_BRACE: '}';
LIST_OPEN: '[';
LIST_CLOSE: ']';

BOOL: 'True' | 'False';
INT: '-'? [0-9]+;
FLOAT: '-'? [0-9]+[.][0-9]* | '-'? [0-9]*[.][0-9]+;
STRING : '"' ( ~["\\] | [\\]. )* '"'
       | '\'' ( ~['\\] | [\\]. )* '\''
       ;
NONE: 'None';

NAME: [a-zA-Z_][a-zA-Z0-9_]*;

WS: [ \t\n\r]+ -> skip;
