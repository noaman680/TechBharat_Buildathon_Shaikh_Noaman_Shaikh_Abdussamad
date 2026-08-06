variable "aws_region" {
  type    = string
  default = "us-east-1"
}

variable "environment" {
  type    = string
  default = "staging"
}

variable "node_count" {
  type    = number
  default = 3
}

variable "db_instance_class" {
  type    = string
  default = "db.t3.medium"
}
