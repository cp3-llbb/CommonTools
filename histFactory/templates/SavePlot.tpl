    if (!m_dataset.is_data)
        {{UNIQUE_NAME}}->Scale({{SAMPLE_SCALE}});
    {{#IN_FOLDER}}outfile->mkdir("{{FOLDER}}"); outfile->cd("{{FOLDER}}");{{/IN_FOLDER}}
    {{UNIQUE_NAME}}->SetName("{{PLOT_NAME}}");
    {{UNIQUE_NAME}}->Write("{{PLOT_NAME}}", TObject::kOverwrite);
    {{#IN_FOLDER}}outfile->cd();{{/IN_FOLDER}}

