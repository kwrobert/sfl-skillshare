DROP TABLE IF EXISTS "users" CASCADE;
CREATE TABLE "users" (
  "id" SERIAL NOT NULL PRIMARY KEY,
  "username" character varying(100) NOT NULL,
  "password" character varying(100) NOT NULL,
  "zipcode" character(5) NOT NULL,
  "color" character varying(20) NOT NULL,
  "age" integer NOT NULL,
  "name" character varying(50) NOT NULL
);
DROP TABLE IF EXISTS "friends";
CREATE TABLE "friends" (
  "id" SERIAL NOT NULL PRIMARY KEY,
  "user_id" int NOT NULL,
  "friend_id" int NOT NULL,
   CONSTRAINT fk_user
       FOREIGN KEY(user_id) 
         REFERENCES users(id) ON DELETE CASCADE,
   CONSTRAINT fk_friend
       FOREIGN KEY(friend_id) 
         REFERENCES users(id) ON DELETE CASCADE
);
