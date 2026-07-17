import os
import uvicorn
from fastapi import FastAPI
from src.middleware.logger_middleware import LoggerMiddleware
from src.routes.todo_routes import router as todo_router
from src.routes.report_routes import router as report_router
from src.routes.user_routes import router as user_router
from src.routes.product_routes import router as product_router
from src.routes.order_routes import router as order_router
from src.routes.review_routes import router as review_router
from src.routes.discount_routes import router as discount_router

app = FastAPI(title="Mock Todo Backend", version="1.0.0")

app.add_middleware(LoggerMiddleware)

app.include_router(todo_router, prefix="/api")
app.include_router(report_router, prefix="/api")
app.include_router(user_router, prefix="/api")
app.include_router(product_router, prefix="/api")
app.include_router(order_router, prefix="/api")
app.include_router(review_router, prefix="/api")
app.include_router(discount_router, prefix="/api")



if __name__ == "__main__":
    port = int(os.getenv("PORT", 3001))
    print(f"Server is running on http://localhost:{port}")
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
