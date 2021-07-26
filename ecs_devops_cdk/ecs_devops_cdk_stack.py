from aws_cdk import core as cdk

# For consistency with other languages, `cdk` is the preferred import name for
# the CDK's core module.  The following line also imports it as `core` for use
# with examples from the CDK Developer's Guide, which are in the process of
# being updated to use `cdk`.  You may delete this import if you don't need it.
from aws_cdk import (
    aws_logs,
    core as cdk,
    aws_ecs as ecs,
    aws_ecr as ecr,
    aws_ec2 as ec2,
    aws_iam as iam
)

ECR_POLICY_ACTIONS = [
    "ecr:GetAuthorizationToken",
    "ecr:BatchCheckLayerAvailability",
    "ecr:GetDownloadUrlForLayer",
    "ecr:BatchGetImage",
    "logs:CreateLogStream",
    "logs:PutLogEvents"
]


class EcsDevopsCdkStack(cdk.Stack):

    def __init__(self, scope: cdk.Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Setting up resources needed

        # Setting up Container Repository
        ecr_repository = ecr.Repository(
            self, "ecs-cdk-repository", repository_name="ecs-cdk-repository")

        # Setting up VPC, in this case we're using an existing one
        vpc = ec2.Vpc.from_lookup(self, "ecs-cdk-vpc", vpc_id="vpc-93f3b8e9")

        # Setting up ECS Cluster with our VPC instance
        cluster = ecs.Cluster(self,
                              "ecs-cdk-cluster",
                              cluster_name="ecs-cdk-cluster",
                              vpc=vpc
                              )

        # Creating execution role used to perform ECS tasks
        execution_role = iam.Role(self,
                                  "ecs-cdk-execution-role",
                                  assumed_by=iam.ServicePrincipal(
                                      "ecs-tasks.amazonaws.com"),
                                  role_name="ecs-cdk-execution-role"
                                  )

        # Attaching policy to give it permissions needed
        execution_role.add_to_policy(iam.PolicyStatement(
            effect=iam.Effect.ALLOW,
            resources=["*"],
            actions=ECR_POLICY_ACTIONS,
        ))

        # Create ECS Task Definition
        task_definition = ecs.FargateTaskDefinition(self,
                                                    "ecs-cdk-task-definition",
                                                    execution_role=execution_role,
                                                    family="ecs-cdk-task-definition"
                                                    )

        # Adding the container
        # Running the task definition with a sample registry
        # Sample container will be replaced with our application container
        # when CI/CD pipeline updates the task definition
        container = task_definition.add_container(
            "ecs-cdk-sandbox",
            image=ecs.ContainerImage.from_registry("amazon/amazon-ecs-sample")
        )

        # Creating Fargate Service
        fargate_service = ecs.FargateService(self,
                                             "ecs-cdk-service",
                                             cluster=cluster,
                                             task_definition=task_definition,
                                             service_name="ecs-cdk-service"
                                             )

        # Creating a Service when instance is in a public subnet
        # fargate_service = ecs.FargateService(self,
        #     "ecs=cdk-service",
        #     cluster=cluster,
        #     task_definition=task_definition,
        #     service_name="ecs-cdk-service",
        #     assign_public_ip=True,
        #     security_group=[List of security groups],
        #     vpc_subnets=[List of subnets]
        # )

        # Creating CloudWatch Log groups
        log_groups = aws_logs.LogGroup(self,
                                       "ecs-cdk-service-log-group",
                                       log_group_name="ecs-cdk-service-logs"
                                       )
