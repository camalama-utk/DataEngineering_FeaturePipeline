
drop table if exists group_project_data;


CREATE TABLE group_project_data (
    salesdate date,
    productid int,
    region text,
    freeship smallint,
    discount float,
    itemssold int
); 

-- create the sql table first, then run data_upload.py file to upload all current csv files
-- and monitor the directory that contains the data to automatically upload new data

