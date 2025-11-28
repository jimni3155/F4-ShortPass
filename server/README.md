# Server Setup Notes

- 기본값은 로컬 S3 시뮬레이터(`server/local_s3_storage`)를 사용합니다.
- 실 AWS S3 연동을 쓰려면 환경변수를 설정합니다:
  - `USE_AWS_S3=true`
  - `S3_BUCKET_NAME=<배포 버킷 이름>`
  - `AWS_REGION=<리전>` (기본 `us-east-1`)
  - 자격 증명은 IAM 역할/환경 변수/credentials 파일 등 표준 `boto3` 경로를 통해 로드됩니다.
- 평가 파이프라인(`/api/v1/interviews/{id}/run-evaluation`) 등 S3 접근이 모두 위 설정을 따릅니다.
- Lambda 실행: `server/lambda_evaluation_handler.lambda_handler`를 배포 후 이벤트 payload에 `company_id`, `job_id`, `applicant_id`, `interview_id`를 포함하면 동일한 파이프라인을 실행합니다 (SQS/EventBridge direct invoke 모두 가능).
