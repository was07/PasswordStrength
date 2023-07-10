import sys
import getpass


colors = {
    "black": "\u001b[30m",
    "red": "\u001b[31m",
    "green": "\u001b[32m",
    "bright green": "\u001b[32;1m",
    "yellow": "\u001b[33m",
    "blue": "\u001b[34m",
    "magenta": "\u001b[35m",
    "cyan": "\u001b[36m",
    "white": "\u001b[37m",
    "gray": "\u001b[30;1m",
    "reset": "\u001b[0m"
}


def form(text: str, color: str, width: int = None):
    if width is not None:
        text = text.ljust(width)
    return colors[color] + text + colors['reset']


class Stat:
    def __init__(self, score: tuple, text: str, *lines: str, color="white", symbol=None): 
        self.score = score
        self.symbol = form('>' if symbol is None else symbol, 'gray')
        self.color = color
        self.text = text
        self.lines = lines
    
    def with_info(self, *lines: str):
        if lines: self.lines = self.lines + lines
        return self


class BoolStat(Stat):
    def __init__(self, value: bool):
        super().__init__((1 if value else 0, 1), 'Yes' if value else 'No', color='white' if value else 'white')
        self.symbol = form('✔' if value else '✖', 'green' if value else 'red')


class PasswordStrengthChecker:
    def __init__(self) -> None:
        ...
    
    def _check(self, password: str) -> dict[str: Stat]:
        res = {}

        upper = 0
        lower = 0
        digits = 0
        symbols = 0
        for char in password:
            if char.islower():
                lower += 1
            elif char.isupper():
                upper += 1
            elif char.isdigit():
                digits += 1
            else:
                symbols += 1
        
        _length = len(password)
        mark = ((14 if _length > 14 else _length) / 14) * 3, 3
        if _length >= 14:
            lengthStat = Stat(mark, "Excellent", "Secure against brute force attacks", color="green")
        elif _length >= 11:
            lengthStat = Stat(mark, "Good", "Secure against brute force attacks", color="green")
        elif _length >= 8:
            lengthStat = Stat(mark, "Short", "Plassibly crackable brute force attacks", color="yellow")
        else:
            lengthStat = Stat(mark, "Too short", "Crackable via brute force attacks", "A length of at least 8 is recommended", color="red")

        with open("10k-most-common.txt", 'r') as f:
            found = password + "\n" in f.readlines()
            res[f"{'A' if found else 'Not a'} common password"] = Stat(
                (-5 if found else 0, 0),
                "COMMON" if found else "Uncommon",
                f"{'CRACKABLE. Found' if found else 'Not found'} in 10,000 most common passwords",
                color="red" if found else "white",
                symbol="✖" if found else ">"
            )
        
        res[f"Length ({len(password)})"] = lengthStat
        res[f"Include: uppercase letters ({upper})"] = BoolStat(upper > 0)
        res[f"Include: lowercase letters ({lower})"] = BoolStat(lower > 0) \
            .with_info(f"{'✔ Has' if upper > 0 and lower > 0 else '✖ Does not have'} mix of upper and lower case.")
        res[f"Include: symbols ({symbols})"] = BoolStat(symbols > 0)
        res[f"Include: numbers ({digits})"] = BoolStat(digits > 0)

        return res
    
    def check(self, password):
        res = self._check(password)
        print("Password: ", form('*' * len(password), 'gray'), '\n')
        
        total_score = 0
        score = 0
        for key, stat in res.items():
            key: str; stat: Stat

            print(stat.symbol+' ', form(stat.text, stat.color, 9), '-', key)

            total_score += stat.score[1]
            score += stat.score[0]
            if stat.lines:
                for line in stat.lines:
                    print(' '*(3+9+2), form(line, 'gray'))
        
        # Scoring
        score = 0 if score < 0 else score
        frac = score / total_score
        if frac >= .8:
            color = 'bright green'
        elif frac >= .6:
            color = "green"
        elif frac >= .5:
            color = 'yellow'
        else:
            color = "red"

        print('\nPassword Strength:', form((str(round(frac * 100, 2))+'%').rjust(44-19), color))

        bar_frac = int(frac * 44)
        print(form('━' * bar_frac, color) + form('━' * (44-bar_frac), 'gray'))


if __name__ == "__main__":
    checker = PasswordStrengthChecker()
    password = getpass.getpass()
    sys.stdout.write("\033[K")  # clear line 
    sys.stdout.write("\033[F")  # back to previous line
    checker.check(password)
