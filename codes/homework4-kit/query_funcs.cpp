/**
citations 
1) https://www.tutorialspoint.com/postgresql/postgresql_c_cpp.htm
**/
#include "query_funcs.h"

#include <iostream>
#include <pqxx/pqxx>

using namespace std;
void initalize_db(connection * C) {
  char * sql =
      "DROP TABLE IF EXISTS COLOR, STATE, TEAM, PLAYER;"
      "CREATE TABLE COLOR(COLOR_ID SERIAL PRIMARY KEY NOT NULL, NAME TEXT "
      "NOT NULL);"
      "CREATE TABLE STATE(STATE_ID SERIAL PRIMARY KEY NOT NULL, NAME TEXT "
      "NOT NULL);"
      "CREATE TABLE TEAM(TEAM_ID SERIAL PRIMARY KEY NOT NULL, NAME TEXT NOT NULL, "
      "STATE_ID INT NOT NULL, COLOR_ID INT NOT NULL, WINS INT, LOOSES INT, "
      "CONSTRAINT FK_STATE_TEAM FOREIGN "
      "KEY(STATE_ID) REFERENCES STATE(STATE_ID) ON DELETE CASCADE,  CONSTRAINT "
      "FK_COLOR_TEAM FOREIGN "
      "KEY(COLOR_ID) REFERENCES COLOR(COLOR_ID) ON DELETE CASCADE);"
      "CREATE TABLE PLAYER(PLAYER_ID SERIAL PRIMARY KEY NOT NULL, TEAM_ID INT NOT NULL, "
      "UNIFORM_NUM INT, FIRST_NAME TEXT, LAST_NAME TEXT, MPG INT, PPG INT, RPG INT, APG "
      "INT, SPG DOUBLE PRECISION, BPG DOUBLE PRECISION, CONSTRAINT FK_TEAM_PLAYER "
      "FOREIGN "
      "KEY(TEAM_ID) REFERENCES TEAM(TEAM_ID) ON DELETE CASCADE);";

  work W(*C);
  W.exec(sql);
  W.commit();
}

void add_player(connection * C,
                int team_id,
                int jersey_num,
                string first_name,
                string last_name,
                int mpg,
                int ppg,
                int rpg,
                int apg,
                double spg,
                double bpg) {
  work W(*C);
  C->prepare("insert_player",
             "INSERT INTO PLAYER (TEAM_ID, UNIFORM_NUM, FIRST_NAME, LAST_NAME, MPG, PPG, "
             "RPG, APG, SPG, BPG) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)");
  W.prepared("insert_player")(team_id)(jersey_num)(first_name)(last_name)(mpg)(ppg)(rpg)(
       apg)(spg)(bpg)
      .exec();
  W.commit();
}

void add_team(connection * C,
              string name,
              int state_id,
              int color_id,
              int wins,
              int losses) {
  work W(*C);
  C->prepare("insert_team",
             "INSERT INTO TEAM (NAME, STATE_ID, COLOR_ID, WINS, LOOSES) VALUES "
             "($1,$2,$3,$4,$5)");
  W.prepared("insert_team")(name)(state_id)(color_id)(wins)(losses).exec();
  W.commit();
}

void add_state(connection * C, string name) {
  work W(*C);
  C->prepare("insert_state", "INSERT INTO STATE (NAME) VALUES ($1)");
  W.prepared("insert_state")(name).exec();
  W.commit();
}

void add_color(connection * C, string name) {
  work W(*C);
  C->prepare("insert_color", "INSERT INTO COLOR (NAME) VALUES ($1)");
  W.prepared("insert_color")(name).exec();
  W.commit();
}

string buildWhereClause(bool whereFlag, int min, int max, string field_name) {
  string where = "";
  if (whereFlag == true) {
    where.append(" AND ");
  }
  where.append(" " + field_name + " >= " + to_string(min) + " AND " + field_name +
               " <= " + to_string(max));

  return where;
}

string buildWhereClause(bool whereFlag, double min, double max, string field_name) {
  string where = "";
  if (whereFlag == true) {
    where.append(" AND ");
  }
  where.append(" " + field_name + " >= " + to_string(min) + " AND " + field_name +
               " <= " + to_string(max));

  return where;
}

/*
 * All use_ params are used as flags for corresponding attributes
 * a 1 for a use_ param means this attribute is enabled (i.e. a WHERE clause is needed)
 * a 0 for a use_ param means this attribute is disabled
 */
void query1(connection * C,
            int use_mpg,
            int min_mpg,
            int max_mpg,
            int use_ppg,
            int min_ppg,
            int max_ppg,
            int use_rpg,
            int min_rpg,
            int max_rpg,
            int use_apg,
            int min_apg,
            int max_apg,
            int use_spg,
            double min_spg,
            double max_spg,
            int use_bpg,
            double min_bpg,
            double max_bpg) {
  string sql = "SELECT PLAYER_ID, TEAM_ID, UNIFORM_NUM, FIRST_NAME, LAST_NAME, MPG, PPG, "
               "RPG, APG, trim(to_char(SPG,'9999999999999990D9')), "
               "trim(to_char(BPG,'99999999999999990D9')) from PLAYER";
  bool whereFlag = false;
  string where = "";
  if (use_mpg == 1) {
    where.append(buildWhereClause(whereFlag, min_mpg, max_mpg, "MPG"));
    whereFlag = true;
  }

  if (use_ppg == 1) {
    where.append(buildWhereClause(whereFlag, min_ppg, max_ppg, "PPG"));
    whereFlag = true;
  }

  if (use_rpg == 1) {
    where.append(buildWhereClause(whereFlag, min_rpg, max_rpg, "RPG"));
    whereFlag = true;
  }

  if (use_apg == 1) {
    where.append(buildWhereClause(whereFlag, min_apg, max_apg, "APG"));
    whereFlag = true;
  }

  if (use_spg == 1) {
    where.append(buildWhereClause(whereFlag, min_spg, max_spg, "SPG"));
    whereFlag = true;
  }

  if (use_bpg == 1) {
    where.append(buildWhereClause(whereFlag, min_bpg, max_bpg, "BPG"));
    whereFlag = true;
  }

  if (whereFlag == true) {
    sql.append(" where " + where);
  }

  cout << "PLAYER_ID TEAM_ID UNIFORM_NUM FIRST_NAME LAST_NAME MPG PPG RPG APG SPG BPG"
       << endl;
  nontransaction N(*C);
  result R(N.exec(sql));

  for (result::const_iterator c = R.begin(); c != R.end(); ++c) {
    cout << c[0] << " " << c[1] << " " << c[2] << " " << c[3] << " " << c[4] << " "
         << c[5] << " " << c[6] << " " << c[7] << " " << c[8] << " " << c[9] << " "
         << c[10] << " " << c[11] << endl;
  }
  C->disconnect();
}

void query2(connection * C, string team_color) {
  nontransaction N(*C);
  C->prepare("query2",
             "SELECT TEAM.NAME FROM TEAM, COLOR WHERE TEAM.COLOR_ID = COLOR.COLOR_ID AND "
             "COLOR.NAME = $1");
  result R(N.prepared("query2")(team_color).exec());

  cout << "NAME" << endl;
  for (result::const_iterator c = R.begin(); c != R.end(); ++c) {
    cout << c[0] << endl;
  }

  C->disconnect();
}

void query3(connection * C, string team_name) {
  nontransaction N(*C);
  C->prepare("query3",
             "SELECT PLAYER.FIRST_NAME, PLAYER.LAST_NAME FROM PLAYER, TEAM WHERE "
             "PLAYER.TEAM_ID = TEAM.TEAM_ID AND TEAM.NAME = $1 ORDER BY PPG DESC");
  result R(N.prepared("query3")(team_name).exec());

  cout << "FIRST_NAME LAST_NAME" << endl;
  for (result::const_iterator c = R.begin(); c != R.end(); ++c) {
    cout << c[0] << " " << c[1] << endl;
  }

  C->disconnect();
}

void query4(connection * C, string team_state, string team_color) {
  nontransaction N(*C);
  C->prepare("query4",
             "SELECT PLAYER.UNIFORM_NUM, PLAYER.FIRST_NAME, PLAYER.LAST_NAME FROM "
             "PLAYER, TEAM, STATE, COLOR WHERE PLAYER.TEAM_ID = TEAM.TEAM_ID AND "
             "TEAM.STATE_ID = STATE.STATE_ID AND COLOR.COLOR_ID = TEAM.COLOR_ID AND "
             "STATE.NAME = $1 AND COLOR.NAME = $2");
  result R(N.prepared("query4")(team_state)(team_color).exec());

  cout << "UNIFORM_NUM FIRST_NAME LAST_NAME" << endl;
  for (result::const_iterator c = R.begin(); c != R.end(); ++c) {
    cout << c[0] << " " << c[1] << " " << c[2] << endl;
  }

  C->disconnect();
}

void query5(connection * C, int num_wins) {
  nontransaction N(*C);
  C->prepare("query5",
             "SELECT PLAYER.FIRST_NAME, PLAYER.LAST_NAME, TEAM.NAME, TEAM.WINS FROM "
             "PLAYER, TEAM WHERE PLAYER.TEAM_ID = TEAM.TEAM_ID AND "
             "TEAM.WINS > $1 ");
  result R(N.prepared("query5")(num_wins).exec());

  cout << "FIRST_NAME LAST_NAME NAME WINS" << endl;
  for (result::const_iterator c = R.begin(); c != R.end(); ++c) {
    cout << c[0] << " " << c[1] << " " << c[2] << " " << c[3] << endl;
  }

  C->disconnect();
}
