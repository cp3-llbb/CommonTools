{
    TObject* obj = plots_directory->Get("{{UNIQUE_NAME}}");
    if (obj) {
        ((TNamed*) obj)->SetName("{{PLOT_NAME}}");
        obj->Write("{{PLOT_NAME}}", TObject::kOverwrite);
        ((TNamed*) obj)->SetName("{{UNIQUE_NAME}}");
    }
}

