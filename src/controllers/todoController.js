const TodoModel = require('../models/todoModel');

class TodoController {
  // GET /api/todos
  static getTodos(req, res) {
    const { q, completed } = req.query;
    const todos = TodoModel.getAll({ q, completed });
    res.json(todos);
  }

  // GET /api/todos/:id
  static getTodoById(req, res) {
    const todo = TodoModel.getById(req.params.id);
    if (!todo) {
      return res.status(404).json({ error: 'Todo not found' });
    }
    res.json(todo);
  }

  // POST /api/todos
  static createTodo(req, res) {
    const { title, completed } = req.body;
    if (!title) {
      return res.status(400).json({ error: 'Title is required' });
    }

    const newTodo = TodoModel.create({ title, completed });
    res.status(201).json(newTodo);
  }

  // PUT /api/todos/:id
  static updateTodo(req, res) {
    const { title, completed } = req.body;
    const updatedTodo = TodoModel.update(req.params.id, { title, completed });

    if (!updatedTodo) {
      return res.status(404).json({ error: 'Todo not found' });
    }

    res.json(updatedTodo);
  }

  // DELETE /api/todos/:id
  static deleteTodo(req, res) {
    const deletedTodo = TodoModel.delete(req.params.id);
    if (!deletedTodo) {
      return res.status(404).json({ error: 'Todo not found' });
    }

    res.json({ message: 'Todo deleted successfully', deletedTodo });
  }
}

module.exports = TodoController;
