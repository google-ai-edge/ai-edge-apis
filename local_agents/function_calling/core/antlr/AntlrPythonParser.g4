parser grammar AntlrPythonParser;


options {
    tokenVocab = AntlrPythonLexer;
}

main: expr EOF;
expr: functionCall+ | functionCallList;

value: INT | FLOAT | BOOL | STRING | NONE | list | dict | object;

list: LIST_OPEN (value (SEP value)*)? LIST_CLOSE;

dict
  : OPEN_BRACE (STRING COLON value (SEP STRING COLON value)*)? CLOSE_BRACE
  ;

argVal: NAME EQ value;
argValExpr: argVal (SEP argVal)*;
object
  : NAME OPEN_PAR CLOSE_PAR
  | NAME OPEN_PAR argValExpr CLOSE_PAR
  ;

emptyFunctionCall: NAME OPEN_PAR CLOSE_PAR;
fullFunctionCall: NAME OPEN_PAR argValExpr CLOSE_PAR;

functionCall
  : fullFunctionCall
  | emptyFunctionCall
  ;

functionCallList: LIST_OPEN functionCall (SEP functionCall)* LIST_CLOSE;