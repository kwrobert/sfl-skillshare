import string
import random
import pprint
import copy
import itertools
import psycopg2
import pymongo
import neo4j


COLORS = [
    "green",
    "blue",
    "black",
    "yellow",
    "orange",
    "gold",
    "silver",
    "purple",
    "pink",
    "red",
]

NAMES = [
    "Kyle",
    "Liam",
    "Noah",
    "Oliver",
    "Elijah",
    "William",
    "James",
    "Benjamin",
    "Lucas",
    "Henry",
    "Alexander",
    "Mason",
    "Michael",
    "Ethan",
    "Daniel",
    "Jacob",
    "Olivia",
    "Emma",
    "Ava",
    "Charlotte",
    "Sophia",
    "Amelia",
    "Isabella",
    "Mia",
    "Evelyn",
    "Harper",
    "Camila",
    "Gianna",
    "Abigail",
    "Luna",
    "Ella",
]


def generate_data(seed=None):
    if seed is not None:
        random.seed(seed)
    users = []
    for i in range(1, 16):
        password_length = random.randint(6, 15)
        password = "".join(
            random.choices(string.ascii_uppercase + string.digits, k=password_length)
        )
        data = {
            "username": f"user{i:03}",
            "password": password,
            "name": random.choice(NAMES),
            "zipcode": f"{random.randint(0, 99999):05}",
            "color": random.choice(COLORS),
            "age": random.randint(1, 100),
        }
        users.append(data)

    inds = list(range(len(users)))
    for i, user in enumerate(users):
        # I guess we're all friends with ourselves but we don't need to store that
        _inds = copy.copy(inds)
        del _inds[i]
        friend_inds = random.choices(_inds, k=random.randint(1, 5))
        friends = [users[j]["username"] for j in friend_inds]
        user["friends"] = friends
    pprint.pprint(users)
    return users

def load_mongo(users):
    """
    """
    client = pymongo.MongoClient("mongodb://root:example@localhost:27017/")
    db = client.sfl
    db.users.insert_many(users)

def load_neo(users):
    """"""

    uri = "neo4j://localhost:7687"
    driver = neo4j.GraphDatabase.driver(uri, auth=("neo4j", "password"))
    
    with driver.session() as session:
        # First create all User nodes
        q = "UNWIND $users AS map CREATE (n:User) SET n = map"
        session.run(q, users=users)
        # Then create the relationships
        # TODO: Optimize this
        q = """
        MATCH 
          (a:User),
          (b:User)
        WHERE a.username = $user1 AND b.username = $user2
        CREATE (a)-[r:FRIEND]->(b)
        """
        for user in users:
            for friend in user['friends']:
                session.run(q, user1=user['username'], user2=friend)

    driver.close()

def load_postgres(users):
    conn = psycopg2.connect(
        host="localhost", port=5433, database="sfl", user="postgres", password="postgres"
    )
    cur = conn.cursor()
    cur.executemany(
        """
    INSERT INTO users (username, password, zipcode, color, age, name)
    VALUES (%(username)s, %(password)s, %(zipcode)s, %(color)s, %(age)s, %(name)s);
    """,
        users,
    )
    conn.commit()
    # TODO: optimize this
    relationships = []
    for user in users:
        cur.execute("SELECT id FROM users WHERE username = %s", (user['username'],))
        result = cur.fetchall()
        user_id = result[0][0]
        placeholder = ','.join('%s' for i in range(len(user['friends'])))
        q = f"SELECT id FROM users WHERE username IN ({placeholder})"
        cur.execute(q, user['friends'])
        friend_ids = [el[0] for el in cur.fetchall()]
        relationships += list(zip(itertools.repeat(user_id), friend_ids))
    cur.executemany(
        """
    INSERT INTO friends (user_id, friend_id)
    VALUES (%s, %s);
    """,
        relationships,
    )
    conn.commit()
    conn.close()

def main():

    users = generate_data(5)
    load_postgres(users)
    load_neo(users)
    # mongo needs to go last because the PyMongo client adds a new field to the
    # dictionaries passed into the insert_many call, which is kind of rude
    load_mongo(users)



if __name__ == "__main__":
    main()
