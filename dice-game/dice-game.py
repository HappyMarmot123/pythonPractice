import random

class Die:
    def __init__(self, sides=6):
        self.sides = sides
        self.value = 1

    def roll(self):
        self.value = random.randint(1, self.sides)
        return self.value

class Player:
    def __init__(self, name):
        self.name = name
        self.die = Die()
        self.score = 0

    def take_turn(self):
        roll_result = self.die.roll()
        self.score = roll_result
        print(f"---{self.name}차례")
        print(f"주사위 값: {self.score}")
        return self.score

def start_dice_game():
    print("---------------------------------")
    print("     환영합니다! 주사위 게임     ")
    print("   더 높은 숫자를 얻는 사람이 승리!   ")
    print("---------------------------------")

    player = Player("루카스")
    computer = Player("컴퓨터")

    player_score = player.take_turn()
    computer_score = computer.take_turn()

    print("--------------최종겷과---------------")
    print(f"당신: {player_score}점 vs. 컴퓨터: {computer_score}점")

    if player_score > computer_score:
        print("🎉 당신의 승리입니다! 🎉")
    elif computer_score > player_score:
        print("💻 컴퓨터의 승리입니다. 다음 기회에!")
    else:
        print("🤝 무승부입니다.")
    print("---------------------------------")
    
if __name__ == "__main__":
    start_dice_game()