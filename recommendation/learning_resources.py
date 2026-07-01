"""
recommendation/learning_resources.py
A curated mapping of skill -> free learning resource(s).
"""

LEARNING_RESOURCES = {
    "Python": [("Python for Everybody (Coursera)", "https://www.coursera.org/specializations/python")],
    "SQL": [("SQL Tutorial (W3Schools)", "https://www.w3schools.com/sql/")],
    "Excel": [("Excel Skills for Business (Coursera)", "https://www.coursera.org/specializations/excel")],
    "Machine Learning": [("Machine Learning by Andrew Ng (Coursera)", "https://www.coursera.org/learn/machine-learning")],
    "Communication": [("Effective Communication (Coursera)", "https://www.coursera.org/learn/wharton-communication-skills")],
    "Git": [("Git & GitHub Crash Course (YouTube)", "https://www.youtube.com/watch?v=RGOj5yH7evk")],
    "Java": [("Java Programming Masterclass (Udemy)", "https://www.udemy.com/course/java-the-complete-java-developer-course/")],
    "REST API": [("REST API Concepts (freeCodeCamp)", "https://www.freecodecamp.org/news/rest-api-tutorial-rest-client-rest-service-and-api-calls-explained-with-code-examples/")],
    "Django": [("Django for Beginners", "https://djangoforbeginners.com/")],
    "Flask": [("Flask Mega-Tutorial", "https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-i-hello-world")],
    "Docker": [("Docker for Beginners", "https://docker-curriculum.com/")],
    "AWS": [("AWS Cloud Practitioner Essentials", "https://aws.amazon.com/training/digital/aws-cloud-practitioner-essentials/")],
    "Pandas": [("Pandas Documentation - Getting Started", "https://pandas.pydata.org/docs/getting_started/index.html")],
    "NumPy": [("NumPy Quickstart", "https://numpy.org/doc/stable/user/quickstart.html")],
    "Data Visualization": [("Data Visualization with Python (Coursera)", "https://www.coursera.org/learn/python-for-data-visualization")],
    "Power BI": [("Power BI Guided Learning (Microsoft)", "https://learn.microsoft.com/en-us/power-bi/guided-learning/")],
    "Tableau": [("Tableau Free Training Videos", "https://www.tableau.com/learn/training")],
    "TensorFlow": [("TensorFlow Tutorials", "https://www.tensorflow.org/tutorials")],
    "PyTorch": [("PyTorch Tutorials", "https://pytorch.org/tutorials/")],
    "Deep Learning": [("Deep Learning Specialization (Coursera)", "https://www.coursera.org/specializations/deep-learning")],
    "Statistics": [("Statistics and Probability (Khan Academy)", "https://www.khanacademy.org/math/statistics-probability")],
    "Problem Solving": [("Problem Solving Techniques (Coursera)", "https://www.coursera.org/learn/problem-solving")],
    "Teamwork": [("Teamwork Skills (LinkedIn Learning)", "https://www.linkedin.com/learning/topics/teamwork")],
    "Leadership": [("Leadership Skills (Coursera)", "https://www.coursera.org/learn/leadership-skills")],
}


def get_resources_for_skill(skill_name: str) -> list[tuple[str, str]]:
    return LEARNING_RESOURCES.get(skill_name, [])