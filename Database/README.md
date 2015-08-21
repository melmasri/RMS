# Database initialization

By default the database is already created and empty in the file `Prod.db`. Nevertheless, if a new clean copy is desired, you can always run the following commands.

* **Windows** double-click on `create_database.bat` or run the following command in this folder 

```
sqlite3 Prod.db < main.sql
```

* **Linux**  run the above command also in this folder, but `sqlite3` should be installed before.

## Database creation steps

The `main.sql` goes through the following steps

1. runs 'create_tables.sql` which would create the following tables:

   * `MAGNITUDE`
   * `EDU_QUAL`
   * `COUNTRY`
   * `REGIONS`
   * `EDU_METER_AID`
   * `EDU_METER97_{REP, OBS, EST}`
   * `EDU_METER97_ NonNumeric_{REP, OBS, EST}`
   * `RM_Mapping`
   * `RM_Mapping_NonNumeric`
   * `DU_INCLUSION_{REP, OBS, EST}`
   * `EDU_COMMENT_TABLE_{REP, OBS, EST}`
   * `EDU_FTN97_{REP}, OBS, EST}`
   
   For more information about the tables refer to `create_tables.sql`.
   
2. runs `insert_data.sql` which insets the data in the folder `/Inserted data` to the following tables:

  * `Inserted data/Qualifier.csv"` to table `EDU_QUAL`
  * `Inserted data/Country.csv"` to table `COUNTRY`
  * `Inserted data/Magnitude(data).csv"` to table `MAGNITUDE`
  * `Inserted data/EDU_METER_AID(data).csv"` to table `EDU_METER_AID`
  * `Inserted data/All AC CODES.csv"` to table `AC_TEMP` and then creates new codes and inserts them into `EDU_METER_AID`
  * `Inserted data/RM_Mapping.csv"` to table `RM_TEMP` and then to `RM_Mapping`
  * `Inserted data/ADM_table.csv"` to table `REGIONS`
  * `Inserted data/RM_Mapping_NonNumeric.csv"` to table `RM_Mapping_NonNumeric`

    For more information about the tables refer to `insert_data.sql`.
## logging and errors

The `main.sql` script is designed to exit the process if any errors are encountered. Before exiting it writes all warnings and errors to the text file `log_sqlite.log`.






