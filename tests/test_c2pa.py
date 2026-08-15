from text_provenance_auditor.c2pa_forensics import parse_manifest_store


def test_parse_valid_manifest_with_provider_hint():
    data = {
        "active_manifest": "urn:test",
        "manifests": {
            "urn:test": {
                "claim_generator": "Claude Example Processor",
                "assertions": [
                    {
                        "label": "c2pa.actions.v2",
                        "data": {
                            "actions": [
                                {
                                    "action": "c2pa.created",
                                    "softwareAgent": "Anthropic Claude",
                                    "digitalSourceType": "http://cv.iptc.org/newscodes/digitalsourcetype/trainedAlgorithmicMedia",
                                }
                            ]
                        },
                    }
                ],
            }
        },
        "validation_status": [],
    }
    report = parse_manifest_store(data, backend="test")
    assert report.manifest_present is True
    assert report.validation_ok is True
    assert report.status == "present_valid"
    assert "anthropic" in report.provider_hints
    assert any("trainedAlgorithmicMedia" in x for x in report.digital_source_types)


def test_parse_manifest_with_validation_warning():
    data = {
        "active_manifest": "urn:test",
        "manifests": {"urn:test": {"claim_generator": "Example"}},
        "validation_status": [{"code": "signingCredential.untrusted"}],
    }
    report = parse_manifest_store(data, backend="test")
    assert report.status == "present_with_validation_warnings"
    assert report.validation_ok is False
