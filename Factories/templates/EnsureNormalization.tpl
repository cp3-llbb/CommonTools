    if (!m_dataset.is_data && (m_dataset.extras_event_weight_sum.count("{{NAME}}") == 0)) {
        throw std::runtime_error("Normalization '{{NAME}}' not found for this dataset");
    }
