-- migrate:up

alter table openapi_server add column base_url varchar;

    -- openapi_path_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    -- spec_id = Column(
    --     UUID(as_uuid=True), ForeignKey("openapi_spec.openapi_spec_id"), nullable=False
    -- )
    -- path_templated = Column(String, nullable=False)





-- migrate:down

alter table openapi_server drop column base_url;
