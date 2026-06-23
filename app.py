import os
import sys


RESET = "\033[0m"
BLUE = "\033[44m\033[97m"
GREEN = "\033[42m\033[30m"


def clear_screen() -> None:
    os.system("cls" if os.name == "nt" else "clear")


def show_screen(message: str, color: str) -> None:
    clear_screen()
    print(f"{color}")
    print("=" * 40)
    print(f"   {message}")
    print("=" * 40)
    print(RESET)
    print("Nhấn Enter để đổi chữ/màu, hoặc gõ q rồi Enter để thoát.")


def main() -> int:
    states = [
        ("Xin chào!", BLUE),
        ("Đã thay đổi rồi!", GREEN),
    ]
    index = 0

    while True:
        message, color = states[index]
        show_screen(message, color)

        user_input = input().strip().lower()
        if user_input == "q":
            clear_screen()
            print("Tạm biệt!")
            return 0

        index = 1 - index


if __name__ == "__main__":
    sys.exit(main())
