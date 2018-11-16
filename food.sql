/*sql 주석을 어떻게 넣는지 모르겠다.
하여간 생성 다 되고, 아마 이거 맞춰서 넣으면 될듯함.
음식별로 테이블 따로 만들려고했는데 솔직히 그건 아니라고봄.*/

CREATE TABLE list(
  category TEXT,
  id INTEGER,
  name TEXT,

  PRIMARY KEY (category, id)
);

CREATE TABLE information(
  category TEXT,
  id INTEGER,
  amount REAL,
  calorie REAL,
  carbohydrate REAL,
  fat REAL,
  protein REAL,
  natrium REAL,
  portion REAL,

  FOREIGN KEY (category, id) REFERENCES list,
  PRIMARY KEY (category, id)
);

CREATE TABLE ir_data(
  category TEXT,
  id INTEGER,
  round INTEGER,
  range INTEGER,
  data REAL,

  FOREIGN KEY (category, id) REFERENCES list,
  PRIMARY KEY (category, id, round, range)
);

CREATE TABLE ir_data_mean(
  category TEXT,
  id INTEGER,
  range INTEGER,
  data REAL,

  FOREIGN KEY (category, id) REFERENCES list,
  PRIMARY KEY (category, id, range)
);