/*******************************************************************************
 * Copyright (c) 2016-2019 Embedded Systems and Applications Group
 * Department of Computer Science, Technische Universitaet Darmstadt,
 * Hochschulstr. 10, 64289 Darmstadt, Germany.
 * <p>
 * All rights reserved.
 * <p>
 * This software is provided free for educational use only.
 * It may not be used for commercial purposes without the
 * prior written permission of the authors.
 ******************************************************************************/
package mavlc.parsing;

import mavlc.errors.SyntaxError;
import mavlc.syntax.SourceLocation;
import mavlc.syntax.expression.*;
import mavlc.syntax.function.FormalParameter;
import mavlc.syntax.function.Function;
import mavlc.syntax.module.Module;
import mavlc.syntax.record.RecordElementDeclaration;
import mavlc.syntax.record.RecordTypeDeclaration;
import mavlc.syntax.statement.*;
import mavlc.syntax.type.*;

import javax.xml.crypto.dsig.TransformService;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Deque;
import java.util.List;
import java.util.function.BinaryOperator;

import static mavlc.parsing.Token.TokenType.*;
import static mavlc.syntax.expression.Compare.Comparison.*;



/**
 * A recursive-descent parser for MAVL.
 */
public final class Parser {

	private final Deque<Token> tokens;
	private Token currentToken;

	/**
	 * @param tokens A token stream that was produced by the {@link Scanner}.
	 */
	public Parser(Deque<Token> tokens) {
		this.tokens = tokens;
		currentToken = tokens.poll();
	}

	/**
	 * Parses the MAVL grammar's start symbol, Module.
	 *
	 * @return A {@link Module} node that is the root of the AST representing the tokenized input program.
	 * @throws SyntaxError to indicate that an unexpected token was encountered.
	 */
	public Module parse() {
		SourceLocation location = currentToken.sourceLocation;

		List<Function> functions = new ArrayList<>();
		List<RecordTypeDeclaration> records = new ArrayList<>();
		while(currentToken.type != EOF) {
			switch(currentToken.type) {
				case FUNCTION:
					functions.add(parseFunction());
					break;
				case RECORD:
					records.add(parseRecordTypeDeclaration());
					break;
				default:
					throw new SyntaxError(currentToken, FUNCTION, RECORD);
			}
		}
		return new Module(location, functions, records);
	}

	private String accept(Token.TokenType type) {
		Token t = currentToken;
		if(t.type != type)
			throw new SyntaxError(t, type);
		acceptIt();
		return t.spelling;
	}

	private void acceptIt() {
		currentToken = tokens.poll();
		if(currentToken == null || currentToken.type == ERROR)
			throw new SyntaxError(currentToken != null ? currentToken : new Token(EOF, null, -1, -1));
	}

	private Function parseFunction() {
		SourceLocation location = currentToken.sourceLocation;

		accept(FUNCTION);
		TypeSpecifier<?> typeSpecifier = parseTypeSpecifier();
		String name = accept(ID);

		List<FormalParameter> parameters = new ArrayList<>();
		List<Statement> body = new ArrayList<>();

		accept(LPAREN);
		if(currentToken.type != RPAREN) {
			parameters.add(parseFormalParameter());
			while(currentToken.type != RPAREN) {
				accept(COMMA);
				parameters.add(parseFormalParameter());
			}
		}
		accept(RPAREN);

		accept(LBRACE);
		while(currentToken.type != RBRACE)
			body.add(parseStatement());
		accept(RBRACE);

		return new Function(location, name, typeSpecifier, parameters, body);
	}

	private FormalParameter parseFormalParameter() {
		SourceLocation location = currentToken.sourceLocation;

		TypeSpecifier<?> typeSpecifier = parseTypeSpecifier();
		String name = accept(ID);

		return new FormalParameter(location, name, typeSpecifier);
	}

	private RecordTypeDeclaration parseRecordTypeDeclaration() {
		SourceLocation location = currentToken.sourceLocation;

		accept(RECORD);
		String name = accept(ID);
		accept(LBRACE);
		List<RecordElementDeclaration> elements = new ArrayList<>();
		// no empty records allowed
		elements.add(parseRecordElementDeclaration());
		while(currentToken.type != RBRACE) {
			elements.add(parseRecordElementDeclaration());
		}
		accept(RBRACE);

		return new RecordTypeDeclaration(location, name, elements);

	}

	private RecordElementDeclaration parseRecordElementDeclaration() {
		SourceLocation location = currentToken.sourceLocation;

		boolean isVariable;
		switch(currentToken.type) {
			case VAL:
				acceptIt();
				isVariable = false;
				break;
			case VAR:
				acceptIt();
				isVariable = true;
				break;
			default:
				throw new SyntaxError(currentToken, VAL, VAR);
		}

		TypeSpecifier<?> typeSpecifier = parseTypeSpecifier();
		String name = accept(ID);
		accept(SEMICOLON);

		return new RecordElementDeclaration(location, isVariable, typeSpecifier, name);

	}

	private IteratorDeclaration parseIteratorDeclaration() {
		SourceLocation location = currentToken.sourceLocation;

		boolean isVariable;
		switch(currentToken.type) {
			case VAL:
				accept(VAL);
				isVariable = false;
				break;
			case VAR:
				accept(VAR);
				isVariable = true;
				break;
			default:
				throw new SyntaxError(currentToken, VAL, VAR);
		}
		TypeSpecifier<?> typeSpecifier = parseTypeSpecifier();
		String name = accept(ID);
		return new IteratorDeclaration(location, name, typeSpecifier, isVariable);
	}

	private TypeSpecifier<?> parseTypeSpecifier() {
		SourceLocation location = currentToken.sourceLocation;

		boolean vector = false;
		switch(currentToken.type) {
			case INT:
				acceptIt();
				return new IntTypeSpecifier(location);
			case FLOAT:
				acceptIt();
				return new FloatTypeSpecifier(location);
			case BOOL:
				acceptIt();
				return new BoolTypeSpecifier(location);
			case VOID:
				acceptIt();
				return new VoidTypeSpecifier(location);
			case STRING:
				acceptIt();
				return new StringTypeSpecifier(location);
			case VECTOR:
				accept(VECTOR);
				vector = true;
				break;
			case MATRIX:
				accept(MATRIX);
				break;
			case ID:
				String name = accept(ID);
				return new RecordTypeSpecifier(location, name);
			default:
				throw new SyntaxError(currentToken, INT, FLOAT, BOOL, VOID, STRING, VECTOR, MATRIX, ID);
		}

		accept(LANGLE);
		TypeSpecifier<?> subtype;
		switch(currentToken.type) {
			case INT:
				subtype = new IntTypeSpecifier(currentToken.sourceLocation);
				break;
			case FLOAT:
				subtype = new FloatTypeSpecifier(currentToken.sourceLocation);
				break;
			default:
				throw new SyntaxError(currentToken, INT, FLOAT);
		}
		acceptIt();
		accept(RANGLE);
		accept(LBRACKET);
		Expression x = parseExpr();
		accept(RBRACKET);

		if(vector)
			return new VectorTypeSpecifier(location, subtype, x);

		accept(LBRACKET);
		Expression y = parseExpr();
		accept(RBRACKET);

		return new MatrixTypeSpecifier(location, subtype, x, y);
	}

	private Statement parseStatement() {
		switch(currentToken.type) {
			case VAL:
				return parseValueDef();
			case VAR:
				return parseVarDecl();
			case RETURN:
				return parseReturn();
			case ID:
				return parseAssignOrCall();
			case FOR:
				return parseFor();
			case FOREACH:
				return parseForEach();
			case IF:
				return parseIf();
			case SWITCH:
				return parseSwitch();
			case LBRACE:
				return parseCompound();
			default:
				throw new SyntaxError(currentToken, VAL, VAR, RETURN, ID, FOR, FOREACH, IF, SWITCH, LBRACE);
		}
	}

	private ValueDefinition parseValueDef() {
		// TODO implement method (task 3.1)
        SourceLocation location = currentToken.sourceLocation;

        accept(VAL);
        TypeSpecifier<?> typeSpecifier = parseTypeSpecifier();
        String name = accept(ID);
        accept(ASSIGN);
        Expression expr = parseExpr();
        accept(SEMICOLON);
        return new ValueDefinition(location, typeSpecifier, name, expr);
	}

	private VariableDeclaration parseVarDecl() {
		// TODO implement method (task 3.1)

        SourceLocation location = currentToken.sourceLocation;
        accept(VAR);
        TypeSpecifier<?> typeSpecifier = parseTypeSpecifier();
        String name = accept(ID);
        accept(SEMICOLON);
        return new VariableDeclaration(location, typeSpecifier, name);
	}

	private ReturnStatement parseReturn() {
		SourceLocation location = currentToken.sourceLocation;
		accept(RETURN);
		Expression e = parseExpr();
		accept(SEMICOLON);

		return new ReturnStatement(location, e);

	}

	private Statement parseAssignOrCall() {
		SourceLocation location = currentToken.sourceLocation;

		String name = accept(ID);

		Statement s;
		if(currentToken.type != LPAREN) {
			s = parseAssign(name, location);
		}
		else {
			s = new CallStatement(location, parseCall(name, location));
		}


		accept(SEMICOLON);

		return s;
	}

    // Problem: Laut Grammatik sind auf der linken Seite einer Zuweisung nicht nur einfache Variablen
    // erlaubt (z.B. x = ...), sondern auch Array-Elemente (x[expr], x[expr][expr]) und Record-Felder
    // (x@feld = ...). Die ursprüngliche Klasse LeftHandIdentifier speichert jedoch nur den reinen
    // Variablennamen und kann daher keine Indizes oder Feldnamen abbilden. Damit die AST-Struktur
    // wirklich das repräsentiert, was die Grammatik zulässt, muss LeftHandIdentifier erweitert werden,
    // sodass er optional eine Liste von Index-Ausdrücken (für Arrays) oder einen Feldnamen (für Records)
    // speichert, und parseAssign muss diese Informationen korrekt in den LeftHandIdentifier einbauen.
    
    private VariableAssignment parseAssign(String name, SourceLocation location) {
		// TODO implement method (task 3.1)
        LeftHandIdentifier lhs = new LeftHandIdentifier(location, name);

        // Verarbeite optionale Index- oder Record-Selektionen
        while (currentToken.type == LBRACKET || currentToken.type == AT) {
            if (currentToken.type == LBRACKET) {
                accept(LBRACKET);
                Expression firstIndex = parseExpr();
                SourceLocation selLoc = currentToken.sourceLocation;
                accept(RBRACKET);
                lhs = new ElementSelect(selLoc, lhs, firstIndex);

                // Zweite Indexauswahl für Matrizen
                if (currentToken.type == LBRACKET) {
                    accept(LBRACKET);
                    Expression secondIndex = parseExpr();
                    selLoc = currentToken.sourceLocation;
                    accept(RBRACKET);
                    lhs = new ElementSelect(selLoc, lhs, secondIndex);
                }
            } else if (currentToken.type == AT) {
                accept(AT);
                String fieldName = accept(ID);
                SourceLocation selLoc = currentToken.sourceLocation;
                lhs = new RecordElementSelect(selLoc, lhs, fieldName);
            }
        }

        // Zuweisung parsen
        accept(ASSIGN);
        Expression expr = parseExpr();

        return new VariableAssignment(location, lhs, expr);
	}

	private CallExpression parseCall(String name, SourceLocation location) {
		accept(LPAREN);

		List<Expression> actualParameters = new ArrayList<>();
		if(currentToken.type != RPAREN) {
			actualParameters.add(parseExpr());
			while(currentToken.type != RPAREN) {
				accept(COMMA);
				actualParameters.add(parseExpr());
			}
		}
		accept(RPAREN);

		return new CallExpression(location, name, actualParameters);

	}

	private ForLoop parseFor() {
		SourceLocation location = currentToken.sourceLocation;

		accept(FOR);
		accept(LPAREN);
		String name = accept(ID);
		accept(ASSIGN);
		Expression a = parseExpr();
		accept(SEMICOLON);
		Expression b = parseExpr();
		accept(SEMICOLON);
		String inc = accept(ID);
		accept(ASSIGN);
		Expression c = parseExpr();
		accept(RPAREN);
		return new ForLoop(location, name, a, b, inc, c, parseStatement());
	}

	private ForEachLoop parseForEach() {
		SourceLocation location = currentToken.sourceLocation;

		accept(FOREACH);
		accept(LPAREN);
		IteratorDeclaration param = parseIteratorDeclaration();
		accept(COLON);
		Expression struct = parseExpr();
		accept(RPAREN);
		return new ForEachLoop(location, param, struct, parseStatement());
	}

	private IfStatement parseIf() {
		SourceLocation location = currentToken.sourceLocation;
		accept(IF);
		accept(LPAREN);
		Expression test = parseExpr();
		accept(RPAREN);
		Statement then = parseStatement();
		if(currentToken.type == ELSE) {
			acceptIt();
			return new IfStatement(location, test, then, parseStatement());
		}
		return new IfStatement(location, test, then);

	}

	private SwitchStatement parseSwitch() {
		// TODO implement method (task 3.5)
        SourceLocation location = currentToken.sourceLocation;
        accept(SWITCH);
        accept(LPAREN);
        Expression test = parseExpr();
        accept(RPAREN);
        accept(LBRACE);

        List<Case> cases = new ArrayList<>();
        List<Default> defaults = new ArrayList<>();

        while(currentToken.type != RBRACE) {
            switch(currentToken.type) {
                case CASE:
                    cases.add(parseCase());
                    break;
                case DEFAULT:
                    defaults.add(parseDefault());
                    break;
                default:
                    throw new SyntaxError(currentToken, CASE, DEFAULT);
            }
        }
        accept(RBRACE);
        return new SwitchStatement(location, test, cases, defaults);
	}

	private Case parseCase() {
		// TODO implement method (task 3.5)
        SourceLocation location = currentToken.sourceLocation;
        accept(CASE);
        Expression expr = parseExpr();
        accept(COLON);
        Statement then = parseStatement();
        return new Case(location, expr, then);
	}

	private Default parseDefault() {
		// TODO implement method (task 3.5)
        SourceLocation location = currentToken.sourceLocation;
        accept(DEFAULT);
        accept(COLON);
        Statement then = parseStatement();
        return new Default(location, then);
	}

	private CompoundStatement parseCompound() {
		// TODO implement method (task 3.3)
        Token lbrace = currentToken;
        accept(LBRACE);
        List<Statement> statements = new ArrayList<>();
        while(currentToken.type != RBRACE){
            statements.add(parseStatement());
        }
        accept(RBRACE);
        return new CompoundStatement(lbrace.sourceLocation, statements);

	}

	private Expression parseExpr() {
		return parseSelect();
	}

	private Expression parseSelect() {
		SourceLocation location = currentToken.sourceLocation;

		Expression cond = parseOr();
		if(currentToken.type == QMARK) {
			acceptIt();
			Expression trueCase = parseOr();
			accept(COLON);
			Expression falseCase = parseOr();
			return new SelectExpression(location, cond, trueCase, falseCase);
		}

		return cond;
	}

	private Expression parseOr() {
		SourceLocation location = currentToken.sourceLocation;

		Expression x = parseAnd();
		while(currentToken.type == OR) {
			acceptIt();
			x = new Or(location, x, parseAnd());
		}
		return x;
	}

	private Expression parseAnd() {
		SourceLocation location = currentToken.sourceLocation;

		Expression x = parseNot();
		while(currentToken.type == AND) {
			acceptIt();
			x = new And(location, x, parseNot());
		}
		return x;
	}

	private Expression parseNot() {
		// TODO extend method (task 3.2)
        SourceLocation location = currentToken.sourceLocation;
        if(currentToken.type == NOT) {
            acceptIt();
            Expression op = parseCompare();
            return new Not(location, op);
        }
		return parseCompare();
	}

	private Expression parseCompare() {
		Expression left = parseAddSub();

		// TODO extend method (task 3.2)
        while (currentToken.type == RANGLE || currentToken.type == LANGLE || currentToken.type == CMPLE || currentToken.type == CMPGE || currentToken.type == CMPEQ || currentToken.type == CMPNE){
            Token op = currentToken;
            acceptIt();

            Expression right = parseAddSub();

            Compare.Comparison comp;
            switch (op.type) {
                case LANGLE: comp = Compare.Comparison.LESS; break;
                case RANGLE: comp = Compare.Comparison.GREATER; break;
                case CMPLE: comp = Compare.Comparison.LESS_EQUAL; break;
                case CMPGE: comp = Compare.Comparison.GREATER_EQUAL; break;
                case CMPEQ: comp = Compare.Comparison.EQUAL; break;
                case CMPNE: comp = Compare.Comparison.NOT_EQUAL; break;
                default: throw new RuntimeException("Unexpected token type for comparison: " + op.type);
            }            left =  new Compare(op.sourceLocation, left, right, comp);
        }
		return left;
	}

	private Expression parseAddSub() {
		SourceLocation location = currentToken.sourceLocation;

		Expression left = parseMulDiv();
		// TODO extend method (task 3.2)
        while(currentToken.type == Token.TokenType.ADD || currentToken.type == Token.TokenType.SUB) {
            Token op = currentToken;
            acceptIt();

            Expression right = parseMulDiv();

            if(op.type == ADD) {
                left = new Addition(location, left, right);
            } else{
                left = new Subtraction(location, left, right);
            }
        }

		return left;
	}

	private Expression parseMulDiv() {
		SourceLocation location = currentToken.sourceLocation;

		Expression left = parseUnaryMinus();
		// TODO extend method (task 3.2)
        while(currentToken.type == Token.TokenType.MULT || currentToken.type == Token.TokenType.DIV) {
            Token op = currentToken;
            acceptIt();

            Expression right = parseUnaryMinus();
            
            if(op.type == Token.TokenType.MULT){
                left = new Multiplication(location, left, right);
            } else{
                left = new Division(location, left, right);
            }
        }
		return left;
	}

	private Expression parseUnaryMinus() {
		// TODO extend method (task 3.2)
        SourceLocation location = currentToken.sourceLocation;

        if(currentToken.type == SUB){
         acceptIt();
         Expression op = parseExponentiation();
         return new UnaryMinus(location, op);
        }
		return parseExponentiation();
	}

	private Expression parseExponentiation() {
		SourceLocation location = currentToken.sourceLocation;

		Expression left = parseDotProd();
		// TODO extend method (task 3.2)
        
        if(currentToken.type == EXP){
            Token op = currentToken;
            acceptIt();
            Expression right = parseExponentiation();
            return new Exponentiation(op.sourceLocation, left, right);
        }
		return left;
	}

	private Expression parseDotProd() {
		SourceLocation location = currentToken.sourceLocation;

		Expression x = parseMatrixMul();
		while(currentToken.type == DOTPROD) {
			acceptIt();
			x = new DotProduct(location, x, parseMatrixMul());
		}
		return x;
	}

	private Expression parseMatrixMul() {
		SourceLocation location = currentToken.sourceLocation;

		Expression x = parseTranspose();
		while(currentToken.type == MATMULT) {
			acceptIt();
			x = new MatrixMultiplication(location, x, parseTranspose());
		}
		return x;
	}

	private Expression parseTranspose() {
		// TODO extend method (task 3.2)
        SourceLocation location = currentToken.sourceLocation;

        if(currentToken.type == TRANSPOSE) {
            acceptIt();
            Expression op = parseDim();
            return new MatrixTranspose(location, op);
        }
        return parseDim();
	}

	private Expression parseDim() {
		SourceLocation location = currentToken.sourceLocation;

		Expression x = parseSubRange();
		switch(currentToken.type) {
			case ROWS:
				acceptIt();
				return new MatrixRows(location, x);
			case COLS:
				acceptIt();
				return new MatrixCols(location, x);
			case DIM:
				acceptIt();
				return new VectorDimension(location, x);
			default:
				return x;
		}
	}

	private Expression parseSubRange() {
		// TODO implement method (task 3.4)
		SourceLocation location = currentToken.sourceLocation;
        Expression x = parseElementSelect();
        if(currentToken.type == LBRACE) {
            accept(LBRACE);
            Expression rStart = parseExpr();
            accept(COLON);
            Expression rStep = parseExpr();
            accept(COLON);
            Expression rEnd = parseExpr();
            accept(RBRACE);
            if(currentToken.type == LBRACE) {
                accept(LBRACE);
                Expression cStart = parseExpr();
                accept(COLON);
                Expression cStep = parseExpr();
                accept(COLON);
                Expression cEnd = parseExpr();
                accept(RBRACE);
            return new SubMatrix(location, x, rStart, rStep, rEnd, cStart, cStep, cEnd);
            } else {
                return new SubVector(location, x, rStart, rStep, rEnd);
            }
        }
        return x;
	}

	private Expression parseElementSelect() {
		SourceLocation location = currentToken.sourceLocation;

		Expression x = parseRecordElementSelect();

		while(currentToken.type == LBRACKET) {
			acceptIt();
			Expression idx = parseExpr();
			accept(RBRACKET);
			x = new ElementSelect(location, x, idx);
		}

		return x;
	}

	private Expression parseRecordElementSelect() {
		SourceLocation location = currentToken.sourceLocation;

		Expression x = parseAtom();

		if(currentToken.type == AT) {
			accept(AT);
			String elementName = accept(ID);
			x = new RecordElementSelect(location, x, elementName);
		}

		return x;

	}

	private Expression parseAtom() {
		SourceLocation location = currentToken.sourceLocation;

		switch(currentToken.type) {
			case INTLIT:
				return new IntValue(location, parseIntLit());
			case FLOATLIT:
				return new FloatValue(location, parseFloatLit());
			case BOOLLIT:
				return new BoolValue(location, parseBoolLit());
			case STRINGLIT:
				return new StringValue(location, accept(STRINGLIT));
			default: /* check other cases below */
		}

		if(currentToken.type == ID) {
			String name = accept(ID);
			if(currentToken.type != LPAREN) {
				return new IdentifierReference(location, name);

			} else {
				return parseCall(name, location);
			}
		}

		if(currentToken.type == LPAREN) {
			acceptIt();
			Expression x = parseExpr();
			accept(RPAREN);
			return x;
		}

		if(currentToken.type == AT) {
			acceptIt();
			String name = accept(ID);
			return new RecordInit(location, name, parseInitializerList());
		}

		if(currentToken.type == LBRACKET) {
			return new StructureInit(location, parseInitializerList());
		}

		throw new SyntaxError(currentToken, INTLIT, FLOATLIT, BOOLLIT, STRINGLIT, ID, LPAREN, LBRACKET, AT);

	}

	private List<Expression> parseInitializerList() {
		List<Expression> elements = new ArrayList<>();

		accept(LBRACKET);
		elements.add(parseExpr());
		while(currentToken.type == COMMA) {
			accept(COMMA);
			elements.add(parseExpr());
		}
		accept(RBRACKET);

		return elements;
	}

	private int parseIntLit() {
		return Integer.parseInt(accept(INTLIT));
	}

	private float parseFloatLit() {
		return Float.parseFloat(accept(FLOATLIT));
	}

	private boolean parseBoolLit() {
		return Boolean.parseBoolean(accept(BOOLLIT));
	}
}
