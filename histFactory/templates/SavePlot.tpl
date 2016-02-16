    if (!m_dataset.is_data)
        {{UNIQUE_NAME}}->Scale({{SAMPLE_SCALE}});
    {{UNIQUE_NAME}}->SetName("{{PLOT_NAME}}");
    {{UNIQUE_NAME}}->Write("{{PLOT_NAME}}", TObject::kOverwrite);

