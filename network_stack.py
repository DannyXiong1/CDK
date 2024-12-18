
from aws_cdk import (
    Stack,
    aws_ec2 as ec2,
)
from constructs import Construct

class CdkLabNetworkStack(Stack):

    @property
    def vpc(self):
        return self.cdk_lab_vpc
    
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Create a VPC with public and private subnets in two availability zones
        self.cdk_lab_vpc = ec2.Vpc(
            self, "cdk_lab_vpc",
            ip_addresses=ec2.IpAddresses.cidr("10.0.0.0/16"),
            subnet_configuration=[
                ec2.SubnetConfiguration(
                    name="PublicSubnet",
                    subnet_type=ec2.SubnetType.PUBLIC
                ),
                ec2.SubnetConfiguration(
                    name="PrivateSubnet",
                    subnet_type=ec2.SubnetType.PRIVATE_WITH_NAT
                )
            ],
            max_azs=2  # Spread across two availability zones
        )
