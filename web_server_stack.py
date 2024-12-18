
from aws_cdk import (
    Stack,
    aws_ec2 as ec2,
    aws_iam as iam,
    aws_rds as rds,
)
from constructs import Construct

class CdkLabWebServerStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, cdk_lab_vpc: ec2.Vpc, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Instance Role with SSM Managed Policy
        instance_role = iam.Role(
            self, "InstanceSSMRole",
            assumed_by=iam.ServicePrincipal("ec2.amazonaws.com"),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name("AmazonSSMManagedInstanceCore")
            ]
        )

        # Security group for web servers
        web_sg = ec2.SecurityGroup(
            self, "WebServerSG",
            vpc=cdk_lab_vpc,
            description="Allow HTTP traffic",
            allow_all_outbound=True
        )
        web_sg.add_ingress_rule(ec2.Peer.any_ipv4(), ec2.Port.tcp(80))

        # Security group for RDS
        rds_sg = ec2.SecurityGroup(
            self, "RDSSG",
            vpc=cdk_lab_vpc,
            description="Allow MySQL traffic from web servers",
            allow_all_outbound=True
        )
        rds_sg.add_ingress_rule(web_sg, ec2.Port.tcp(3306))

        # Launch EC2 instances in public subnets
        for i, subnet in enumerate(cdk_lab_vpc.select_subnets(subnet_type=ec2.SubnetType.PUBLIC).subnets):
            ec2.Instance(
                self, f"WebServerInstance{i + 1}",
                vpc=cdk_lab_vpc,
                vpc_subnets=ec2.SubnetSelection(subnets=[subnet]),
                instance_type=ec2.InstanceType("t2.micro"),
                machine_image=ec2.AmazonLinuxImage(),
                role=instance_role,
                security_group=web_sg
            )

        # RDS instance
        rds_instance = rds.DatabaseInstance(
            self, "MySQLInstance",
            engine=rds.DatabaseInstanceEngine.mysql(version=rds.MysqlEngineVersion.VER_8_0_28),
            vpc=cdk_lab_vpc,
            vpc_subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PRIVATE_WITH_NAT),
            security_groups=[rds_sg],
            instance_type=ec2.InstanceType("t3.micro"),
            multi_az=False,
            allocated_storage=20,
            max_allocated_storage=100,
            database_name="MyAppDB",
            publicly_accessible=False
        )
