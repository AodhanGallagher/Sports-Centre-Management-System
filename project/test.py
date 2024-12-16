"""Module for unit testing"""
import os
import unittest
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from app import app, db, models
import datetime

# create a test case that will be used for all tests.
class TestCase(unittest.TestCase):
    # sets up the test case to allow for database manipulation and a local host.
    def setUp(self):
        app.config.from_object('config')
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
        self.app = app.test_client()
        db.create_all()
        pass

    # clears up the database upon the end of the tests.
    def tearDown(self):
        db.session.remove()
        db.drop_all()

    # checks if the app has been created successfully.
    def test_app(self):
        assert self.app is not None

    # group of tests to check if the routes for a user who is not logged in
    # are functioning correctly, each test checks if the page returns properly
    # and then if the associated route is correct.
    def test_loggedOutRoutes(self):
        # creates a user account, to check with employee route later.
        response = self.app.post('/registration', data={'forename': 'user', 'surname' :'user',
                                  'username': 'userOne', 'email': 'userOne@test.com',
                                  'password': 'userPassword', 'confirmPassword': 'userPassword'},
                                  follow_redirects = True)

        # checks the base route.
        response = self.app.get('/',
                                follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.request.url, 'http://localhost/')

        # checks the login route.
        response = self.app.get('/login',
                                follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.request.url, 'http://localhost/login')

        # checks the logout route, should return to the base route.
        response = self.app.get('/logout',
                                follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.request.url, 'http://localhost/')

        # checks the registration route, should return to the registration route.
        response = self.app.get('/registration',
                              follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.request.url, 'http://localhost/registration')

        # checks the account route, should return the base route.
        response = self.app.get('/account',
                                follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.request.url, 'http://localhost/')

        # checks the change password route, should return to the base route.
        response = self.app.get('/change_password',
                                follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.request.url, 'http://localhost/')

        # checks the dashboard route, should return to the base route.
        response = self.app.get('/dashboard',
                                follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.request.url, 'http://localhost/')

        # checks the employee route, should return to the base route.
        response = self.app.get('/employee',
                                follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.request.url, 'http://localhost/')

        # checks the employee user route, should return to the base route.
        response= self.app.get('/employee/1',
                               follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.request.url, 'http://localhost/')

        # checks the management route, should return to the base route.
        response = self.app.get('/management',
                                follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.request.url, 'http://localhost/')

        # checks the monthly membership route, should return to the base route.
        response = self.app.get('/monthly_membership',
                                follow_redirects = True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.request.url, 'http://localhost/')

        # checks the yearly membership route, should return to the base route.
        response = self.app.get('/annual_membership',
                                follow_redirects = True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.request.url, 'http://localhost/')

    # group of tests to check if the routes for a user who is logged in
    # are functioning correctly, each test checks if the page returns properly
    # and then if the associated route is correct.
    def test_loggedInUserRoutes(self):
        # creates a user account, to check with employee route later.
        response = self.app.post('/registration', data={'forename': 'user', 'surname' :'user',
                                  'username': 'userOne', 'email': 'userOne@test.com',
                                  'password': 'userPassword', 'confirmPassword': 'userPassword'},
                                  follow_redirects = True)

        # creates a user account, checks if it is created correctly, should return to the login route.
        response = self.app.post('/registration', data={'forename': 'test', 'surname' :'testing',
                                  'username': 'testUser', 'email': 'test@test.com',
                                  'password': 'testPassword', 'confirmPassword': 'testPassword'},
                                  follow_redirects = True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.request.url, 'http://localhost/login')

        # logs in a user using the created account, checks if it logs in correctly, should return the dashboard route.
        response = self.app.post('/login', data={'username': 'testUser', 'password': 'testPassword',
                                                 'remember_me': False}, 
                                                 follow_redirects = True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.request.url, 'http://localhost/dashboard')

        # checks the login route, should return to the base route.
        response = self.app.get('/login',
                                follow_redirects = True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.request.url, 'http://localhost/')

        # checks the registration route, should return to the base route.
        response = self.app.get('/registration',
                                follow_redirects = True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.request.url, 'http://localhost/')

        # checks the account route, should return the account route.
        response = self.app.get('/account',
                                follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.request.url, 'http://localhost/account')

        # checks the change password route, should return the change password route.
        response = self.app.get('/change_password',
                                follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.request.url, 'http://localhost/change_password')
        
        # checks the dashboard route, should return to that user's dashboard route.
        response = self.app.get('/dashboard', 
                                follow_redirects = True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.request.url, 'http://localhost/dashboard')

        # checks the employee route, should return to the base route.
        response = self.app.get('/employee',
                                follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.request.url, 'http://localhost/')

        # checks the employee user route, should return to the base route.
        response= self.app.get('/employee/1',
                               follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.request.url, 'http://localhost/')

        # checks the management route, should return to the base route.
        response = self.app.get('/management',
                                follow_redirects = True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.request.url, 'http://localhost/')

        # checks the monthly membership route, should send a stripe API call.
        response = self.app.get('/monthly_membership')
        self.assertEqual(response.status_code, 303)
        self.assertEqual(response.request.url, 'http://localhost/monthly_membership')

        # checks the yearly membership route, should send a stripe API call.
        response = self.app.get('/annual_membership')
        self.assertEqual(response.status_code, 303)
        self.assertEqual(response.request.url, 'http://localhost/annual_membership')

        # checks the logout route, should log out the user and return to the base route.
        response = self.app.get('/logout',
                                follow_redirects = True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.request.url, 'http://localhost/')

        # checks the dashboard route, to check if the user has logged out correctly, should return to the base route.
        response = self.app.get('/dashboard',
                                follow_redirects = True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.request.url, 'http://localhost/')

    # group of tests to check if the routes for an employee who is logged in
    # are functioning correctly, each test checks if the page returns properly
    # and then if the associated route is correct.
    def test_loggedInEmployeeRoutes(self):
        # creates a user account, to check with employee route later.
        response = self.app.post('/registration', data={'forename': 'user', 'surname' :'user',
                                  'username': 'userOne', 'email': 'userOne@test.com',
                                  'password': 'userPassword', 'confirmPassword': 'userPassword'},
                                  follow_redirects = True)

        # creates an employee account, checks if it is created correctly, should return to the login route.
        response = self.app.post('/registration', data={'forename': 'test', 'surname' :'testing',
                                  'username': 'testUser', 'email': 'test@test.com',
                                  'password': 'testPassword', 'confirmPassword': 'testPassword'},
                                  follow_redirects = True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.request.url, 'http://localhost/login')

        # adds the correct privilege to the newly created employee account.
        testAccount = models.Account.query.filter_by(username='testUser').first()
        testAccount.privilege = 1
        db.session.commit()

        # logs in an employee using the created account, checks if it logs in correctly, should return the dashboard route.
        response = self.app.post('/login', data={'username': 'testUser', 'password': 'testPassword',
                                                 'remember_me': False}, 
                                                 follow_redirects = True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.request.url, 'http://localhost/dashboard')

        # checks the login route, should return to the base route.
        response = self.app.get('/login',
                                follow_redirects = True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.request.url, 'http://localhost/')

        # checks the registration route, should return to the base route.
        response = self.app.get('/registration',
                                follow_redirects = True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.request.url, 'http://localhost/')

        # checks the account route, should return the account route.
        response = self.app.get('/account',
                                follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.request.url, 'http://localhost/account')

        # checks the change password route, should return the change password route.
        response = self.app.get('/change_password',
                                follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.request.url, 'http://localhost/change_password')
        
        # checks the dashboard route, should return to that employee's dashboard route.
        response = self.app.get('/dashboard', 
                                follow_redirects = True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.request.url, 'http://localhost/dashboard')

        # checks the employee route, should return the employee route.
        response = self.app.get('/employee',
                                follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.request.url, 'http://localhost/employee')

        # checks the employee user route, should return the employee user route.
        response= self.app.get('/employee/1',
                               follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.request.url, 'http://localhost/employee/1')

        # checks the management route, should return to the base route.
        response = self.app.get('/management',
                                follow_redirects = True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.request.url, 'http://localhost/')

        # checks the monthly membership route, should send a stripe API call.
        response = self.app.get('/monthly_membership')
        self.assertEqual(response.status_code, 303)
        self.assertEqual(response.request.url, 'http://localhost/monthly_membership')

        # checks the yearly membership route, should send a stripe API call.
        response = self.app.get('/annual_membership')
        self.assertEqual(response.status_code, 303)
        self.assertEqual(response.request.url, 'http://localhost/annual_membership')

        # checks the logout route, should log out the user and return to the base route.
        response = self.app.get('/logout',
                                follow_redirects = True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.request.url, 'http://localhost/')

        # checks the dashboard route, to check if the employee has logged out correctly, should return to the base route.
        response = self.app.get('/dashboard',
                                follow_redirects = True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.request.url, 'http://localhost/')

    # group of tests to check if the routes for a manager who is logged in
    # are functioning correctly, each test checks if the page returns properly
    # and then if the associated route is correct.
    def test_loggedInManagerRoutes(self):
        # creates a user account, to check with employee route later.
        response = self.app.post('/registration', data={'forename': 'user', 'surname' :'user',
                                  'username': 'userOne', 'email': 'userOne@test.com',
                                  'password': 'userPassword', 'confirmPassword': 'userPassword'},
                                  follow_redirects = True)

        # creates a manager account, checks if it is created correctly, should return to the login route.
        response = self.app.post('/registration', data={'forename': 'test', 'surname' :'testing',
                                  'username': 'testUser', 'email': 'test@test.com',
                                  'password': 'testPassword', 'confirmPassword': 'testPassword'},
                                  follow_redirects = True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.request.url, 'http://localhost/login')

        # adds the correct privilege to the newly created manager account.
        testAccount = models.Account.query.filter_by(username='testUser').first()
        testAccount.privilege = 2
        db.session.commit()

        # logs in a manager using the created account, checks if it logs in correctly, should return the dashboard route.
        response = self.app.post('/login', data={'username': 'testUser', 'password': 'testPassword',
                                                 'remember_me': False}, 
                                                 follow_redirects = True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.request.url, 'http://localhost/dashboard')

        # checks the login route, should return to the base route.
        response = self.app.get('/login',
                                follow_redirects = True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.request.url, 'http://localhost/')

        # checks the registration route, should return to the base route.
        response = self.app.get('/registration',
                                follow_redirects = True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.request.url, 'http://localhost/')

        # checks the account route, should return the account route.
        response = self.app.get('/account',
                                follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.request.url, 'http://localhost/account')

        # checks the change password route, should return the change password route.
        response = self.app.get('/change_password',
                                follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.request.url, 'http://localhost/change_password')
        
        # checks the dashboard route, should return to that manager's dashboard route.
        response = self.app.get('/dashboard', 
                                follow_redirects = True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.request.url, 'http://localhost/dashboard')

        # checks the employee route, should return to the base route.
        response = self.app.get('/employee',
                                follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.request.url, 'http://localhost/employee')

        # checks the employee user route, should return the employee user route.
        response= self.app.get('/employee/1',
                               follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.request.url, 'http://localhost/employee/1')

        # checks the management route, should return to the base route.
        response = self.app.get('/management',
                                follow_redirects = True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.request.url, 'http://localhost/management')

        # checks the monthly membership route, should send a stripe API call.
        response = self.app.get('/monthly_membership')
        self.assertEqual(response.status_code, 303)
        self.assertEqual(response.request.url, 'http://localhost/monthly_membership')

        # checks the yearly membership route, should send a stripe API call.
        response = self.app.get('/annual_membership')
        self.assertEqual(response.status_code, 303)
        self.assertEqual(response.request.url, 'http://localhost/annual_membership')

        # checks the logout route, should log out the manager and return to the base route.
        response = self.app.get('/logout',
                                follow_redirects = True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.request.url, 'http://localhost/')

        # checks the dashboard route, to check if the user has logged out correctly, should return to the base route.
        response = self.app.get('/dashboard',
                                follow_redirects = True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.request.url, 'http://localhost/')

    def testRegistrationForm(self):
        # runs registration form correctly, to check if the form will submit, should return to login route.
        response = self.app.post('/registration', data={'forename': 'test', 'surname' :'testing',
                                                        'username': 'testUser', 'email': 'test@test.com',
                                                        'password': 'testPassword', 'confirmPassword': 'testPassword'},
                                                        follow_redirects = True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.request.url, 'http://localhost/login')

        # runs registration form with a mising forename, to check if the form will error, should return to registration route.
        response = self.app.post('/registration', data={'forename': '', 'surname' : 'testingTwo',
                                                        'username': 'testTwoUser', 'email':'testTwo@test.com',
                                                        'password': 'testPassword', 'confirmPassword': 'testPassword'},
                                                        follow_redirects = True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.request.url, 'http://localhost/registration')

        # runs registration form with a mising surname, to check if the form will error, should return to registration route.
        response = self.app.post('/registration', data={'forename': 'testTwo', 'surname' : '',
                                                        'username': 'testTwoUser', 'email':'testTwo@test.com',
                                                        'password': 'testPassword', 'confirmPassword': 'testPassword'},
                                                        follow_redirects = True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.request.url, 'http://localhost/registration')

        # runs registration form with a mising username, to check if the form will error, should return to registration route.
        response = self.app.post('/registration', data={'forename': 'testTwo', 'surname' : 'testingTwo',
                                                        'username': '', 'email':'testTwo@test.com',
                                                        'password': 'testPassword', 'confirmPassword': 'testPassword'},
                                                        follow_redirects = True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.request.url, 'http://localhost/registration')

        # runs registration form with a mising email, to check if the form will error, should return to registration route.
        response = self.app.post('/registration', data={'forename': 'testTwo', 'surname' : 'testingTwo',
                                                        'username': 'testTwoUser', 'email':'',
                                                        'password': 'testPassword', 'confirmPassword': 'testPassword'},
                                                        follow_redirects = True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.request.url, 'http://localhost/registration')

        # runs registration form with a mising password, to check if the form will error, should return to registration route.
        response = self.app.post('/registration', data={'forename': 'testTwo', 'surname' : 'testingTwo',
                                                        'username': 'testTwoUser', 'email':'testTwo@test.com',
                                                        'password': '', 'confirmPassword': 'testPassword'},
                                                        follow_redirects = True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.request.url, 'http://localhost/registration')

        # runs registration form with a mising confirmation password, to check if the form will error, should return to registration route.
        response = self.app.post('/registration', data={'forename': 'testTwo', 'surname' : 'testingTwo',
                                                        'username': 'testTwoUser', 'email':'testTwo@test.com',
                                                        'password': 'testPassword', 'confirmPassword': ''},
                                                        follow_redirects = True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.request.url, 'http://localhost/registration')

        # runs registration form with a too long forename, to check if the form will error, should return to registration route.
        response = self.app.post('/registration', data={'forename': 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa', 'surname' : 'testingTwo',
                                                        'username': 'testTwoUser', 'email':'testTwo@test.com',
                                                        'password': 'testPassword', 'confirmPassword': 'testPassword'},
                                                        follow_redirects = True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.request.url, 'http://localhost/registration')

        # runs registration form with a too long surname, to check if the form will error, should return to registration route.
        response = self.app.post('/registration', data={'forename': 'testTwo', 'surname' : 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa',
                                                        'username': 'testTwoUser', 'email':'testTwo@test.com',
                                                        'password': 'testPassword', 'confirmPassword': 'testPassword'},
                                                        follow_redirects = True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.request.url, 'http://localhost/registration')
        
        # runs registration form with a too short username, to check if the form will error, should return to registration route.
        response = self.app.post('/registration', data={'forename': 'testTwo', 'surname' : 'testingTwo',
                                                        'username': 'a', 'email':'testTwo@test.com',
                                                        'password': 'testPassword', 'confirmPassword': 'testPassword'},
                                                        follow_redirects = True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.request.url, 'http://localhost/registration')

        # runs registration form with a too long username, to check if the form will error, should return to registration route.
        response = self.app.post('/registration', data={'forename': 'testTwo', 'surname' : 'testingTwo',
                                                        'username': 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa', 
                                                        'email':'testTwo@test.com',
                                                        'password': 'testPassword', 'confirmPassword': 'testPassword'},
                                                        follow_redirects = True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.request.url, 'http://localhost/registration')

        # runs registration form with a too short email, to check if the form will error, should return to registration route.
        response = self.app.post('/registration', data={'forename': 'testTwo', 'surname' : 'testingTwo',
                                                        'username': 'testTwoUser', 'email':'t@',
                                                        'password': 'testPassword', 'confirmPassword': 'testPassword'},
                                                        follow_redirects = True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.request.url, 'http://localhost/registration')

        # runs registration form with a too short password, to check if the form will error, should return to registration route.
        response = self.app.post('/registration', data={'forename': 'testTwo', 'surname' : 'testingTwo',
                                                        'username': 'testTwoUser', 'email':'testTwo@test.com',
                                                        'password': 'test', 'confirmPassword': 'test'},
                                                        follow_redirects = True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.request.url, 'http://localhost/registration')

        # runs registration form with a too long email, to check if the form will error, should return to registration route.
        response = self.app.post('/registration', data={'forename': 'testTwo', 'surname' : 'testingTwo',
                                                        'username': 'testTwoUser', 'email':'testTwo@test.com',
                                                        'password': 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa', 'confirmPassword': 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'},
                                                        follow_redirects = True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.request.url, 'http://localhost/registration')

        # runs registration form with an identical username, to check if the form will error, should return to registration route.
        response = self.app.post('/registration', data={'forename': 'testTwo', 'surname' : 'testingTwo',
                                                        'username': 'testUser', 'email':'testTwo@test.com',
                                                        'password': 'testPassword', 'confirmPassword': 'testPassword'},
                                                        follow_redirects = True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.request.url, 'http://localhost/registration')

        # runs registration form with an identical email, to check if the form will error, should return to registration route.
        response = self.app.post('/registration', data={'forename': 'testTwo', 'surname' : 'testingTwo',
                                                        'username': 'testUserTwo', 'email':'test@test.com',
                                                        'password': 'testPassword', 'confirmPassword': 'testPassword'},
                                                        follow_redirects = True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.request.url, 'http://localhost/registration')

        # runs registration form with an invalid email, to check if the form will error, should return to registration route.
        response = self.app.post('/registration', data={'forename': 'testTwo', 'surname' : 'testingTwo',
                                                        'username': 'testUserTwo', 'email':'testTwo',
                                                        'password': 'testPassword', 'confirmPassword': 'testPassword'},
                                                        follow_redirects = True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.request.url, 'http://localhost/registration')

        # runs registration form with a mismatched password, to check if the form will error, should return to registration route.
        response = self.app.post('/registration', data={'forename': 'testTwo', 'surname' : 'testingTwo',
                                                        'username': 'testUserTwo', 'email':'testTwo',
                                                        'password': 'testPassword', 'confirmPassword': 'testPasswordTwo'},
                                                        follow_redirects = True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.request.url, 'http://localhost/registration')        

    def testLoginForm(self):
        # runs registration form, to create a user for testing purposes, should return to login route.
        response = self.app.post('/registration', data={'forename': 'test', 'surname' :'testing',
                                                        'username': 'testUser', 'email': 'test@test.com',
                                                        'password': 'testPassword', 'confirmPassword': 'testPassword'},
                                                        follow_redirects = True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.request.url, 'http://localhost/login')

        # runs login form with a missing username, to check if the form will error, should return to login route.
        response = self.app.post('/login', data={'username': '', 'password': 'testPassword',
                                                 'remember_me': False},
                                                follow_redirects = True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.request.url, 'http://localhost/login')

        # runs login form with incorrect username, to check if the form will error, should return to login route.
        response = self.app.post('/login', data={'username': 'testUser', 'password': '',
                                                 'remember_me': False},
                                                follow_redirects = True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.request.url, 'http://localhost/login')

        # runs login form with incorrect username, to check if the form will error, should return to login route.
        response = self.app.post('/login', data={'username': 'testTwo', 'password': 'testPassword',
                                                 'remember_me': False},
                                                follow_redirects = True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.request.url, 'http://localhost/login')

        # runs login form with incorrect password, to check if the form will error, should return to login route.
        response = self.app.post('/login', data={'username': 'testUser', 'password': 'testTwoPassword',
                                                 'remember_me': False},
                                                 follow_redirects = True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.request.url, 'http://localhost/login')

        # runs login form correctly, to check if the form will submit, should return to dashboard route.
        response = self.app.post('/login', data={'username': 'testUser', 'password': 'testPassword',
                                                 'remember_me': False},
                                                 follow_redirects = True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.request.url, 'http://localhost/dashboard')

    def testChangePasswordForm(self):
        # creates a manager account, to allow for no permission conflicts.
        self.app.post('/registration', data={'forename': 'test', 'surname': 'testing',
                                             'username': 'testUser', 'email': 'test@test.com',
                                             'password': 'testPassword', 'confirmPassword': 'testPassword'},
                                             follow_redirects = True)
        
        # adds the correct privilege to the newly created manager account.
        testAccount = models.Account.query.filter_by(username='testUser').first()
        testAccount.privilege = 2
        db.session.commit()

        # logs in a manager using the created account, to allow access to the management page..
        self.app.post('/login', data={'username': 'testUser', 'password': 'testPassword',
                                      'remember_me': False}, 
                                      follow_redirects = True)
        # runs change_password form incorrectly with empty password and confirmPassword, to check if the form will error, should remain on change_password route.
        response = self.app.post('/change_password', data={'password': '', 'confirmPassword': ''},
                                                           follow_redirects = True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.request.url, 'http://localhost/change_password')

        # runs change_password form incorrectly with mismatched passwords, to check if the form will error, should remain on change_password route.
        response = self.app.post('/change_password', data={'password': 'oldPassword', 'confirmPassword': 'newPassword'},
                                                           follow_redirects = True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.request.url, 'http://localhost/change_password')

        # runs change_password form incorrectly with too small passwords, to check if the form will error, should remain on change_password route.
        response = self.app.post('/change_password', data={'password': 'Pass', 'confirmPassword': 'Pass'},
                                 follow_redirects = True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.request.url, 'http://localhost/change_password')

        # runs change_password form incorrectly with too large passwords, to check if the form will error, should remain on change_password route.
        response = self.app.post('/change_password', data={'password': 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa', 
                                                           'confirmPassword': 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'},
                                                           follow_redirects = True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.request.url, 'http://localhost/change_password')

        # runs change_password form correctly, to check if the form submits, should
        response = self.app.post('/change_password', data={'password': 'newPassword', 'confirmPassword': 'newPassword'},
                                                           follow_redirects = True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.request.url, 'http://localhost/account') 

    def testUserForm(self):
        # creates a user account, to check with user form later.
        self.app.post('/registration', data={'forename': 'user', 'surname' :'user',
                                             'username': 'userOne', 'email': 'userOne@test.com',
                                             'password': 'userPassword', 'confirmPassword': 'userPassword'},
                                             follow_redirects = True)

        # creates a manager account, to allow for access to the management page later.
        self.app.post('/registration', data={'forename': 'test', 'surname': 'testing',
                                             'username': 'testUser', 'email': 'test@test.com',
                                             'password': 'testPassword', 'confirmPassword': 'testPassword'},
                                             follow_redirects = True)
        
        # adds the correct privilege to the newly created manager account.
        testAccount = models.Account.query.filter_by(username='testUser').first()
        testAccount.privilege = 2
        db.session.commit()

        # logs in a manager using the created account, to allow access to the management page..
        self.app.post('/login', data={'username': 'testUser', 'password': 'testPassword',
                                      'remember_me': False}, 
                                      follow_redirects = True)

        # runs user form incorrectly with a blank forename, to check if the form will error, forename should remain test.
        response = self.app.post('/management', data={'id' : 1, 'forename': '', 'surname': 'testing',
                                                      'username': 'testUser', 'email': 'test@test.com',
                                                      'privilege': 2},
                                                      follow_redirects = True)
        testAccount = models.Account.query.filter_by(username='testUser').first()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(testAccount.forename, 'test')

        # runs user form incorrectly with a blank surname, to check if the form will error, surname should remain testing.
        response = self.app.post('/management', data={'id' : 1, 'forename': 'test', 'surname': '',
                                                      'username': 'testUser', 'email': 'test@test.com',
                                                      'privilege': 2},
                                                      follow_redirects = True)
        testAccount = models.Account.query.filter_by(username='testUser').first()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(testAccount.surname, 'testing')

        # runs user form incorrectly with a blank username, to check if the form will error, username should remain testUser.
        response = self.app.post('/management', data={'id' : 1, 'forename': 'test', 'surname': 'testing',
                                                      'username': '', 'email': 'test@test.com',
                                                      'privilege': 2},
                                                      follow_redirects = True)
        testAccount = models.Account.query.filter_by(forename='test').first()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(testAccount.username, 'testUser')

        # runs user form incorrectly with a blank email, to check if the form will error, email should remain test@test.com.
        response = self.app.post('/management', data={'id' : 1, 'forename': 'test', 'surname': 'testing',
                                                      'username': 'testUser', 'email': '',
                                                      'privilege': 2},
                                                      follow_redirects = True)
        testAccount = models.Account.query.filter_by(username='testUser').first()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(testAccount.email, 'test@test.com')

        # runs user form incorrectly with a too small email, to check if the form will error, email should remain test@test.com.
        response = self.app.post('/management', data={'id' : 1, 'forename': 'test', 'surname': 'testing',
                                                      'username': 'testUser', 'email': 't@t',
                                                      'privilege': 2},
                                                      follow_redirects = True)
        testAccount = models.Account.query.filter_by(username='testUser').first()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(testAccount.email, 'test@test.com')

        # runs user form incorrectly with a too large forename, to check if the form will error, forename should remain test.
        response = self.app.post('/management', data={'id' : 1, 'forename': 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa', 'surname': 'testing',
                                                      'username': 'testUser', 'email': 'test@test.com',
                                                      'privilege': 2},
                                                      follow_redirects = True)
        testAccount = models.Account.query.filter_by(username='testUser').first()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(testAccount.forename, 'test')

        # runs user form incorrectly with a too large surname, to check if the form will error, surname should remain testing.
        response = self.app.post('/management', data={'id' : 1, 'forename': 'test', 'surname': 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa',
                                                      'username': 'testUser', 'email': 'test@test.com',
                                                      'privilege': 2},
                                                      follow_redirects = True)
        testAccount = models.Account.query.filter_by(username='testUser').first()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(testAccount.surname, 'testing')

        # runs user form incorrectly with a too large username, to check if the form will error, username should remain testUser.
        response = self.app.post('/management', data={'id' : 1, 'forename': 'test', 'surname': 'testing',
                                                      'username': 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa',
                                                      'email': 'test@test.com',
                                                      'privilege': 2},
                                                      follow_redirects = True)
        testAccount = models.Account.query.filter_by(forename='test').first()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(testAccount.username, 'testUser')

        # runs user form incorrectly with an invalid privilege, to check if the form will error, privilege should remain 2.
        response = self.app.post('/management', data={'id' : 1, 'forename': 'test', 'surname': 'testing',
                                                      'username': 'testUser', 'email': 'test@test.com',
                                                      'privilege': 5},
                                                      follow_redirects = True)
        testAccount = models.Account.query.filter_by(username='testUser').first()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(testAccount.privilege, 2)

        # runs user form correctly to add a new user, to check if the database updates correctly, id should be 3.
        response = self.app.post('/management', data={'id': '', 'forename': 'new', 'surname': 'acc',
                                                      'username': 'newAcc', 'email': 'newAcc@test.com',
                                                      'privilege': 1},
                                                      follow_redirects = True)
        testAccount = models.Account.query.filter_by(username='newAcc').first()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(testAccount.id, 3)

        # runs user form correctly with an edited forename, to check if the database updates correctlty, forename should match userTest.
        response = self.app.post('/management', data={'id': 1, 'forename': 'userTest', 'surname': 'user',
                                           'username': 'userOne', 'email': 'userOne@test.com',
                                           'privilege': 0},
                                           follow_redirects = True)
        testAccount = models.Account.query.filter_by(username='userOne').first()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(testAccount.forename, 'userTest')


# allows code to be run when the file is called.
if __name__ == '__main__':
    unittest.main()
