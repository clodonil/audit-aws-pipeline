from templates.pipelines import pipeline_success, pipeline_faild
import tools


for y in range(2):
   num_pipeline = 2
   account      = tools.generate_account()
   pipeline     = tools.generate_name()
   execution_id = tools.generate_execution_id()
   pipeline_id  = tools.generate_execution_id()
   region       = 'us-east-1'
   pipelines    =  pipeline_success(account, execution_id,pipeline,region, pipeline_id)
   tools.save_sqs(pipelines,region)


#for y in range(1):
#    num_pipeline = 2
#    account      = tools.generate_account()
#    pipeline     = tools.generate_name()
#    execution_id = tools.generate_execution_id()
#    pipeline_id  = tools.generate_execution_id()
#    region       = 'us-east-1'
#    pipelines    =  pipeline_faild(account, execution_id,pipeline,region, pipeline_id)
#    tools.save_sqs(pipelines,region)
#    print(pipeline)

   #print_pipeline(pipelines)