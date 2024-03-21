# SECche
Quickly and easily get the past financial reports from a company!

Project available on the web: [SECche website](https://secche.skoshche.com)

---
## About the Project
I created SECche in order for there to be a free way to quickly and easily get the fundamental analytics of a company. All of the information is provided free of charge from the SEC's website using their own API, the only work that I have done myself is try to present it in a nice format.

To use this project, all you will need to do is enter the company's ticker. At the moment the CIK number is provided by a large database provided by @jadchaar. In the future, I hope to find an updated method rather than a static database. Some smaller companies may not show up for the time being.

I will be honest, I have never done anything on GitHub before and I am learning so please be patient with me, I hope to keep this maintained and cleaner in the future :)

---

## Usage
Example
```py
import SECche
from typing import Final

apiInstance: Final[Secche] = Secche()
apiInstance.query("aapl")
```
---

<img width="1258" alt="Screenshot 2024-03-17 at 3 52 28 AM" src="https://github.com/Skoshche/SECche/assets/136208576/f685410c-127e-46fc-87f1-c1253f5396b3">
