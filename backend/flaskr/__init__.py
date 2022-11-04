import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def paginate(request, selection):
    page = request.args.get('page', 1, type=int)
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE
    items = [item.format() for item in selection]
    current_page = items[start:end]
    return current_page

def create_app(test_config=None):
  # create and configure the app
	app = Flask(__name__)
	setup_db(app)
  
	CORS(app, resources={r"/": {"origins": "*"}})

	@app.after_request
	def after_request(response):
		'''
        Sets access control.
        '''
		response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,true')
		response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
		return response


	@app.route('/categories')
	def get_categories():
		categories = Category.query.all()
		return jsonify({
			'categories': {category.id: category.type for category in categories},
			'message': 'success'
		}, 200)


	@app.route('/questions')
	def get_questions():
		questions = Question.query.all()
		current_questions = paginate(request, questions)
		categories = Category.query.all()
		categories_obj = {category.id: category.type for category in categories}
		return jsonify({
            'message': 'success',
            'questions': current_questions,
            'totalQuestions': len(questions),
            'categories': categories_obj,
			'currentCategory': None
        }, 200)


	@app.route("/questions/<question_id>", methods=['DELETE'])
	def delete_question(question_id):
		try:
			question = Question.query.get(question_id)
			question.delete()
			return jsonify({
				'message': 'Success',
				'deleted': question_id
				}, 200)
		except Exception as e:
			return jsonify({
				'message': 'Failed',
			}, 400)


	@app.route("/questions", methods=['POST'])
	def add_question():
		data = request.get_json()
		question = data.get('question', None)
		answer = data.get('answer', None)
		difficulty = data.get('difficulty', None)
		category = data.get('category', None)

		if not all([question, answer, difficulty, category]):
			return jsonify({
				"message": "Missing fields, "
				"expected fields [question, answer, difficulty, category]"
			}, 400)

		question = Question(
			question=question,
			answer=answer,
            difficulty=difficulty,
			category=category
		)
		question.insert()
		return jsonify({
			'message': 'success',
			'question': question.id
		}, 201)


	@app.route('/questions/search', methods=['POST'])
	def search_questions():
		data = request.get_json()
		search_term = data.get('searchTerm', None)
		results = []
		if search_term:
			results = Question.query.filter(Question.question.ilike(f'%{search_term}%')).all()
		return jsonify({
			'message': 'success',
			'questions': [question.format() for question in results],
			'totalQuestions': len(results),
			'currentCategory': None
		}, 200)


	@app.route('/categories/<int:category_id>/questions', methods=['GET'])
	def get_questions_by_category(category_id):
		category = Category.query.filter_by(id=id).one_or_none()
		if category:
			questions = Question.query.filter(Question.category == category.id).all()
			return jsonify({
				'message': 'success',
				'questions': [question.format() for question in questions],
				'totalQuestions': len(questions),
				'currentCategory': category_id
			}, 200)
		return jsonify({
			'message': f'Category {category_id} not found',
		}, 404)


	'''
	@TODO: 
	Create a POST endpoint to get questions to play the quiz. 
	This endpoint should take category and previous question parameters 
	and return a random questions within the given category, 
	if provided, and that is not one of the previous questions. 

	TEST: In the "Play" tab, after a user selects "All" or a category,
	one question at a time is displayed, the user is allowed to answer
	and shown whether they were correct or not. 
	'''

	'''
	@TODO: 
	Create error handlers for all expected errors 
	including 404 and 422. 
	'''
  
	return app

    