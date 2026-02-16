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

import static mavlc.parsing.Token.TokenType.ADD;
import static mavlc.parsing.Token.TokenType.AND;
import static mavlc.parsing.Token.TokenType.ASSIGN;
import static mavlc.parsing.Token.TokenType.AT;
import static mavlc.parsing.Token.TokenType.BOOL;
import static mavlc.parsing.Token.TokenType.BOOLLIT;
import static mavlc.parsing.Token.TokenType.CASE;
import static mavlc.parsing.Token.TokenType.CMPEQ;
import static mavlc.parsing.Token.TokenType.CMPGE;
import static mavlc.parsing.Token.TokenType.CMPLE;
import static mavlc.parsing.Token.TokenType.CMPNE;
import static mavlc.parsing.Token.TokenType.COLON;
import static mavlc.parsing.Token.TokenType.COMMA;
import static mavlc.parsing.Token.TokenType.DEFAULT;
import static mavlc.parsing.Token.TokenType.DIV;
import static mavlc.parsing.Token.TokenType.DOTPROD;
import static mavlc.parsing.Token.TokenType.ELSE;
import static mavlc.parsing.Token.TokenType.EOF;
import static mavlc.parsing.Token.TokenType.ERROR;
import static mavlc.parsing.Token.TokenType.EXP;
import static mavlc.parsing.Token.TokenType.FLOAT;
import static mavlc.parsing.Token.TokenType.FLOATLIT;
import static mavlc.parsing.Token.TokenType.FOR;
import static mavlc.parsing.Token.TokenType.FOREACH;
import static mavlc.parsing.Token.TokenType.FUNCTION;
import static mavlc.parsing.Token.TokenType.ID;
import static mavlc.parsing.Token.TokenType.IF;
import static mavlc.parsing.Token.TokenType.INT;
import static mavlc.parsing.Token.TokenType.INTLIT;
import static mavlc.parsing.Token.TokenType.LANGLE;
import static mavlc.parsing.Token.TokenType.LBRACE;
import static mavlc.parsing.Token.TokenType.LBRACKET;
import static mavlc.parsing.Token.TokenType.LPAREN;
import static mavlc.parsing.Token.TokenType.MATMULT;
import static mavlc.parsing.Token.TokenType.MATRIX;
import static mavlc.parsing.Token.TokenType.MULT;
import static mavlc.parsing.Token.TokenType.NOT;
import static mavlc.parsing.Token.TokenType.OR;
import static mavlc.parsing.Token.TokenType.QMARK;
import static mavlc.parsing.Token.TokenType.RANGLE;
import static mavlc.parsing.Token.TokenType.RBRACE;
import static mavlc.parsing.Token.TokenType.RBRACKET;
import static mavlc.parsing.Token.TokenType.RECORD;
import static mavlc.parsing.Token.TokenType.RETURN;
import static mavlc.parsing.Token.TokenType.RPAREN;
import static mavlc.parsing.Token.TokenType.SEMICOLON;
import static mavlc.parsing.Token.TokenType.STRING;
import static mavlc.parsing.Token.TokenType.STRINGLIT;
import static mavlc.parsing.Token.TokenType.SUB;
import static mavlc.parsing.Token.TokenType.SWITCH;
import static mavlc.parsing.Token.TokenType.TRANSPOSE;
import static mavlc.parsing.Token.TokenType.VAL;
import static mavlc.parsing.Token.TokenType.VAR;
import static mavlc.parsing.Token.TokenType.VECTOR;
import static mavlc.parsing.Token.TokenType.VOID;
import static mavlc.syntax.expression.Compare.Comparison.EQUAL;
import static mavlc.syntax.expression.Compare.Comparison.GREATER;
import static mavlc.syntax.expression.Compare.Comparison.GREATER_EQUAL;
import static mavlc.syntax.expression.Compare.Comparison.LESS;
import static mavlc.syntax.expression.Compare.Comparison.LESS_EQUAL;
import static mavlc.syntax.expression.Compare.Comparison.NOT_EQUAL;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.Deque;
import java.util.List;

import mavlc.errors.SyntaxError;
import mavlc.syntax.SourceLocation;
import mavlc.syntax.expression.Addition;
import mavlc.syntax.expression.And;
import mavlc.syntax.expression.BoolValue;
import mavlc.syntax.expression.CallExpression;
import mavlc.syntax.expression.Compare;
import mavlc.syntax.expression.Division;
import mavlc.syntax.expression.DotProduct;
import mavlc.syntax.expression.ElementSelect;
import mavlc.syntax.expression.Exponentiation;
import mavlc.syntax.expression.Expression;
import mavlc.syntax.expression.FloatValue;
import mavlc.syntax.expression.IdentifierReference;
import mavlc.syntax.expression.IntValue;
import mavlc.syntax.expression.MatrixCols;
import mavlc.syntax.expression.MatrixMultiplication;
import mavlc.syntax.expression.MatrixRows;
import mavlc.syntax.expression.MatrixTranspose;
import mavlc.syntax.expression.Multiplication;
import mavlc.syntax.expression.Not;
import mavlc.syntax.expression.Or;
import mavlc.syntax.expression.RecordElementSelect;
import mavlc.syntax.expression.RecordInit;
import mavlc.syntax.expression.SelectExpression;
import mavlc.syntax.expression.StringValue;
import mavlc.syntax.expression.StructureInit;
import mavlc.syntax.expression.SubMatrix;
import mavlc.syntax.expression.SubVector;
import mavlc.syntax.expression.Subtraction;
import mavlc.syntax.expression.UnaryMinus;
import mavlc.syntax.expression.VectorDimension;
import mavlc.syntax.function.FormalParameter;
import mavlc.syntax.function.Function;
import mavlc.syntax.module.Module;
import mavlc.syntax.record.RecordElementDeclaration;
import mavlc.syntax.record.RecordTypeDeclaration;
import mavlc.syntax.statement.CallStatement;
import mavlc.syntax.statement.Case;
import mavlc.syntax.statement.CompoundStatement;
import mavlc.syntax.statement.Default;
import mavlc.syntax.statement.ForEachLoop;
import mavlc.syntax.statement.ForLoop;
import mavlc.syntax.statement.IfStatement;
import mavlc.syntax.statement.IteratorDeclaration;
import mavlc.syntax.statement.LeftHandIdentifier;
import mavlc.syntax.statement.MatrixLhsIdentifier;
import mavlc.syntax.statement.RecordLhsIdentifier;
import mavlc.syntax.statement.ReturnStatement;
import mavlc.syntax.statement.Statement;
import mavlc.syntax.statement.SwitchStatement;
import mavlc.syntax.statement.ValueDefinition;
import mavlc.syntax.statement.VariableAssignment;
import mavlc.syntax.statement.VariableDeclaration;
import mavlc.syntax.type.BoolTypeSpecifier;
import mavlc.syntax.type.FloatTypeSpecifier;
import mavlc.syntax.type.IntTypeSpecifier;
import mavlc.syntax.type.MatrixTypeSpecifier;
import mavlc.syntax.type.RecordTypeSpecifier;
import mavlc.syntax.type.StringTypeSpecifier;
import mavlc.syntax.type.TypeSpecifier;
import mavlc.syntax.type.VectorTypeSpecifier;
import mavlc.syntax.type.VoidTypeSpecifier;

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
	 * @return A {@link Module} node that is the root of the AST representing the
	 *         tokenized input program.
	 * @throws SyntaxError to indicate that an unexpected token was encountered.
	 */
	public Module parse() {
		SourceLocation location = currentToken.sourceLocation;

		List<Function> functions = new ArrayList<>();
		List<RecordTypeDeclaration> records = new ArrayList<>();
		while (currentToken.type != EOF) {
			switch (currentToken.type) {
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
		if (t.type != type)
			throw new SyntaxError(t, type);
		acceptIt();
		return t.spelling;
	}

	private void acceptIt() {
		currentToken = tokens.poll();
		if (currentToken == null || currentToken.type == ERROR)
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
		if (currentToken.type != RPAREN) {
			parameters.add(parseFormalParameter());
			while (currentToken.type != RPAREN) {
				accept(COMMA);
				parameters.add(parseFormalParameter());
			}
		}
		accept(RPAREN);

		accept(LBRACE);
		while (currentToken.type != RBRACE)
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
		while (currentToken.type != RBRACE) {
			elements.add(parseRecordElementDeclaration());
		}
		accept(RBRACE);

		return new RecordTypeDeclaration(location, name, elements);

	}

	private RecordElementDeclaration parseRecordElementDeclaration() {
		SourceLocation location = currentToken.sourceLocation;

		boolean isVariable;
		switch (currentToken.type) {
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
		switch (currentToken.type) {
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
		switch (currentToken.type) {
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
		switch (currentToken.type) {
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

		if (vector)
			return new VectorTypeSpecifier(location, subtype, x);

		accept(LBRACKET);
		Expression y = parseExpr();
		accept(RBRACKET);

		return new MatrixTypeSpecifier(location, subtype, x, y);
	}

	private Statement parseStatement() {
		switch (currentToken.type) {
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
		// DONE implement method (task 3.1)
		SourceLocation location = currentToken.sourceLocation;
		accept(VAL);
		TypeSpecifier<?> typeSpecifier = parseTypeSpecifier();
		String name = accept(ID);
		accept(ASSIGN);
		Expression e = parseExpr();
		accept(SEMICOLON);

		return new ValueDefinition(location, typeSpecifier, name, e);
	}

	private VariableDeclaration parseVarDecl() {
		// DONE implement method (task 3.1)
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
		if (currentToken.type != LPAREN) {
			s = parseAssign(name, location);
		} else {
			s = new CallStatement(location, parseCall(name, location));
		}

		accept(SEMICOLON);

		return s;
	}

	private VariableAssignment parseAssign(String name, SourceLocation location) {
		// DONE implement method (task 3.1)

		Expression rowIndex = null;
		Expression colIndex = null;
		String recordElementName = null;

		if (currentToken.type == LBRACKET) {
			if (currentToken.type == LBRACKET) {
				accept(LBRACKET);
				rowIndex = parseExpr();
				accept(RBRACKET);

				if (currentToken.type == LBRACKET) {
					accept(LBRACKET);
					colIndex = parseExpr();
					accept(RBRACKET);
				}
			}
		} else if (currentToken.type == AT) {
			accept(AT);
			recordElementName = accept(ID);
		}

		accept(ASSIGN);
		Expression e = parseExpr();

		LeftHandIdentifier lhs;

		if (rowIndex != null) {
			lhs = new MatrixLhsIdentifier(location, name, rowIndex, colIndex);
		} else if (recordElementName != null) {
			lhs = new RecordLhsIdentifier(location, name, recordElementName);
		} else {
			lhs = new LeftHandIdentifier(location, name);
		}

		return new VariableAssignment(location, lhs, e);
	}

	private CallExpression parseCall(String name, SourceLocation location) {
		accept(LPAREN);

		List<Expression> actualParameters = new ArrayList<>();
		if (currentToken.type != RPAREN) {
			actualParameters.add(parseExpr());
			while (currentToken.type != RPAREN) {
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
		if (currentToken.type == ELSE) {
			acceptIt();
			return new IfStatement(location, test, then, parseStatement());
		}
		return new IfStatement(location, test, then);

	}

	private SwitchStatement parseSwitch() {
		// DONE implement method (task 3.5)
		SourceLocation location = currentToken.sourceLocation;
		List<Case> cases = new ArrayList<>();
		List<Default> defaults = new ArrayList<>();

		accept(SWITCH);
		accept(LPAREN);
		Expression condition = parseExpr();
		accept(RPAREN);
		accept(LBRACE);
		while (currentToken.type != RBRACE) {
			if (currentToken.type == CASE) {
				cases.add(parseCase());
			} else if (currentToken.type == DEFAULT) {
				defaults.add(parseDefault());
			}
		}
		accept(RBRACE);
		return new SwitchStatement(location, condition, cases, defaults);
	}

	private Case parseCase() {
		// DONE implement method (task 3.5)
		SourceLocation location = currentToken.sourceLocation;

		accept(CASE);
		Expression condition = parseExpr();
		accept(COLON);
		Statement statement = parseStatement();

		return new Case(location, condition, statement);
	}

	private Default parseDefault() {
		// DONE implement method (task 3.5)
		SourceLocation location = currentToken.sourceLocation;

		accept(DEFAULT);
		accept(COLON);
		Statement statement = parseStatement();

		return new Default(location, statement);
	}

	private CompoundStatement parseCompound() {
		// DONE implement method (task 3.3)
		SourceLocation location = currentToken.sourceLocation;
		List<Statement> list = new ArrayList<>();
		accept(LBRACE);
		while (currentToken.type != RBRACE) {
			list.add(parseStatement());
		}
		accept(RBRACE);
		return new CompoundStatement(location, list);
	}

	private Expression parseExpr() {
		return parseSelect();
	}

	private Expression parseSelect() {
		SourceLocation location = currentToken.sourceLocation;

		Expression cond = parseOr();
		if (currentToken.type == QMARK) {
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
		while (currentToken.type == OR) {
			acceptIt();
			x = new Or(location, x, parseAnd());
		}
		return x;
	}

	private Expression parseAnd() {
		SourceLocation location = currentToken.sourceLocation;

		Expression x = parseNot();
		while (currentToken.type == AND) {
			acceptIt();
			x = new And(location, x, parseNot());
		}
		return x;
	}

	private Expression parseNot() {
		// DONE extend method (task 3.2)
		SourceLocation location = currentToken.sourceLocation;

		if (currentToken.type == NOT) {
			acceptIt();
			Expression operand = parseCompare();
			return new Not(location, operand);
		} else {
			return parseCompare();
		}
	}

	private Expression parseCompare() {
		SourceLocation location = currentToken.sourceLocation;

		Expression x = parseAddSub();

		List<Token.TokenType> list = Arrays.asList(RANGLE, LANGLE, CMPLE, CMPGE, CMPEQ, CMPNE);
		// DONE extend method (task 3.2)
		while (list.contains(currentToken.type)) {
			switch (currentToken.type) {
				case RANGLE:
					acceptIt();
					x = new Compare(location, x, parseAddSub(), GREATER);
					break;
				case LANGLE:
					acceptIt();
					x = new Compare(location, x, parseAddSub(), LESS);
					break;
				case CMPLE:
					acceptIt();
					x = new Compare(location, x, parseAddSub(), LESS_EQUAL);
					break;
				case CMPGE:
					acceptIt();
					x = new Compare(location, x, parseAddSub(), GREATER_EQUAL);
					break;
				case CMPEQ:
					acceptIt();
					x = new Compare(location, x, parseAddSub(), EQUAL);
					break;
				case CMPNE:
					acceptIt();
					x = new Compare(location, x, parseAddSub(), NOT_EQUAL);
					break;
				default:
			}
		}
		return x;
	}

	private Expression parseAddSub() {
		SourceLocation location = currentToken.sourceLocation;

		Expression x = parseMulDiv();
		// DONE extend method (task 3.2)
		List<Token.TokenType> list = Arrays.asList(ADD, SUB);
		while (list.contains(currentToken.type)) {
			switch (currentToken.type) {
				case ADD:
					acceptIt();
					x = new Addition(location, x, parseMulDiv());
					break;
				case SUB:
					acceptIt();
					x = new Subtraction(location, x, parseMulDiv());
					break;
				default:
			}
		}
		return x;
	}

	private Expression parseMulDiv() {
		SourceLocation location = currentToken.sourceLocation;

		Expression x = parseUnaryMinus();
		// DONE extend method (task 3.2)
		List<Token.TokenType> list = Arrays.asList(MULT, DIV);
		while (list.contains(currentToken.type)) {
			switch (currentToken.type) {
				case MULT:
					acceptIt();
					x = new Multiplication(location, x, parseUnaryMinus());
					break;
				case DIV:
					acceptIt();
					x = new Division(location, x, parseUnaryMinus());
					break;
				default:
			}
		}
		return x;
	}

	private Expression parseUnaryMinus() {
		// DONE extend method (task 3.2)
		SourceLocation location = currentToken.sourceLocation;
		if (currentToken.type == SUB) {
			acceptIt();
			return new UnaryMinus(location, parseExponentiation());
		}
		return parseExponentiation();
	}

	private Expression parseExponentiation() {
		// DONE extend method (task 3.2)
		SourceLocation location = currentToken.sourceLocation;

		Expression left = parseDotProd();
		while (currentToken.type == EXP) {
			acceptIt();
			Expression right = parseExponentiation();
			return new Exponentiation(location, left, right);
		}
		return left;
	}

	private Expression parseDotProd() {
		SourceLocation location = currentToken.sourceLocation;

		Expression x = parseMatrixMul();
		while (currentToken.type == DOTPROD) {
			acceptIt();
			x = new DotProduct(location, x, parseMatrixMul());
		}
		return x;
	}

	private Expression parseMatrixMul() {
		SourceLocation location = currentToken.sourceLocation;

		Expression x = parseTranspose();
		while (currentToken.type == MATMULT) {
			acceptIt();
			x = new MatrixMultiplication(location, x, parseTranspose());
		}
		return x;
	}

	private Expression parseTranspose() {
		SourceLocation location = currentToken.sourceLocation;
		// DONE extend method (task 3.2)
		if (currentToken.type == TRANSPOSE) {
			accept(TRANSPOSE);
			return new MatrixTranspose(location, parseDim());
		}
		return parseDim();
	}

	private Expression parseDim() {
		SourceLocation location = currentToken.sourceLocation;

		Expression x = parseSubRange();
		switch (currentToken.type) {
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
		// DONE implement method (task 3.4)
		SourceLocation location = currentToken.sourceLocation;

		Expression x = parseElementSelect();

		if (currentToken.type == LBRACE) {
			accept(LBRACE);
			Expression xStartIndex = parseExpr();
			accept(COLON);
			Expression xBaseIndex = parseExpr();
			accept(COLON);
			Expression xEndIndex = parseExpr();
			accept(RBRACE);

			if (currentToken.type == LBRACE) {
				accept(LBRACE);
				Expression yStartIndex = parseExpr();
				accept(COLON);
				Expression yBaseIndex = parseExpr();
				accept(COLON);
				Expression yEndIndex = parseExpr();
				accept(RBRACE);
				return new SubMatrix(location, x, xBaseIndex, xStartIndex, xEndIndex, yBaseIndex, yStartIndex, yEndIndex);
			}
			return new SubVector(location, x, xBaseIndex, xStartIndex, xEndIndex);
		}

		return x;
	}

	private Expression parseElementSelect() {
		SourceLocation location = currentToken.sourceLocation;

		Expression x = parseRecordElementSelect();

		while (currentToken.type == LBRACKET) {
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

		if (currentToken.type == AT) {
			accept(AT);
			String elementName = accept(ID);
			x = new RecordElementSelect(location, x, elementName);
		}

		return x;

	}

	private Expression parseAtom() {
		SourceLocation location = currentToken.sourceLocation;

		switch (currentToken.type) {
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

		if (currentToken.type == ID) {
			String name = accept(ID);
			if (currentToken.type != LPAREN) {
				return new IdentifierReference(location, name);

			} else {
				return parseCall(name, location);
			}
		}

		if (currentToken.type == LPAREN) {
			acceptIt();
			Expression x = parseExpr();
			accept(RPAREN);
			return x;
		}

		if (currentToken.type == AT) {
			acceptIt();
			String name = accept(ID);
			return new RecordInit(location, name, parseInitializerList());
		}

		if (currentToken.type == LBRACKET) {
			return new StructureInit(location, parseInitializerList());
		}

		throw new SyntaxError(currentToken, INTLIT, FLOATLIT, BOOLLIT, STRINGLIT, ID, LPAREN, LBRACKET, AT);

	}

	private List<Expression> parseInitializerList() {
		List<Expression> elements = new ArrayList<>();

		accept(LBRACKET);
		elements.add(parseExpr());
		while (currentToken.type == COMMA) {
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
