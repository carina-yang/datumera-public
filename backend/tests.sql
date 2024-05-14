" SELECT '" + context.dmStageOdsCostsSciTableName+ "', COUNT(1)
 FROM " +  context.DMConnectionReadWrite_SchemaStagingLayer+"."+context.dmStageOdsCostsSciTableName+
"  WHERE etl_data_source = 'ADJ_COSTS' and  etl_last_updated_date >= '" + ((String)globalMap.get("startTime")) + "'

 UNION

  SELECT '" + context.dmStageOdsSalesSciTableName+ "', COUNT(1)
 FROM " +  context.DMConnectionReadWrite_SchemaStagingLayer+"."+context.dmStageOdsSalesSciTableName+
"  WHERE etl_data_source = 'ADJ_SALES' and  etl_last_updated_date >= '" + ((String)globalMap.get("startTime")) + "'
union

 SELECT '" + context.dmStageOdsPandLSciTableName+ "', COUNT(1)
 FROM " +  context.DMConnectionReadWrite_SchemaStagingLayer+"."+context.dmStageOdsPandLSciTableName+
"  WHERE etl_data_source = 'ADJ_PANDL' and  etl_last_updated_date >= '" + ((String)globalMap.get("startTime")) + "'
 UNION
 
  SELECT '" + context.dmStageOdsCoGSSciTableName+ "', COUNT(1)
 FROM " +  context.DMConnectionReadWrite_SchemaStagingLayer+"."+context.dmStageOdsCoGSSciTableName+
"  WHERE etl_data_source = 'ADJ_COGS' and  etl_last_updated_date >= '" + ((String)globalMap.get("startTime")) + "'"