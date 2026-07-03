const express = require('express');
const router = express.Router();
const TodoController = require('../controllers/todoController');

// Define routes and bind them to controller methods
router.get('/todos', TodoController.getTodos);
router.get('/todos/stats', TodoController.getTodoStats);
router.delete('/todos/completed', TodoController.clearCompletedTodos);
router.get('/todos/:id', TodoController.getTodoById);
router.post('/todos', TodoController.createTodo);
router.put('/todos/:id', TodoController.updateTodo);
router.patch('/todos/:id', TodoController.updateTodo);
router.post('/todos/:id/toggle', TodoController.toggleTodo);
router.delete('/todos/:id', TodoController.deleteTodo);

module.exports = router;
