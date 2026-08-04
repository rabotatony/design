"""
machine.py — the orchestrator. One call runs the entire loop on a project:
mine -> (human: signature+rhythm) -> compose -> verify -> apply -> verify ->
code scan -> content scan -> unified report.

The machine proposes; humans approve. Every stage reports evidence.
"""
import json
import dna_miner
import composer
import design_scan
import apply
import code_detector
import corpus_detector


def run_machine(css, texts, content_sources, code_files, content_collections,
                human_signature, human_rhythm):
    report = {'stages': {}}
    mined = dna_miner.mine_project(css, texts, content_sources)
    report['stages']['mine'] = {
        'dna': mined['dna'], 'confidence': mined['confidence'],
        'needs_human': mined['needs_human']}
    dna = {
        'material': mined['dna'].get('material'),
        'palette_logic': mined['dna'].get('palette_logic'),
        'voice': mined['dna'].get('voice'),
        'motif': mined['dna'].get('motif'),
        'hierarchy_logic': 'emanation: content descends like the sefirot',
        'signature': human_signature,
        'rhythm_logic': human_rhythm,
    }
    report['stages']['dna'] = {'human_added': ['signature', 'rhythm_logic'], 'dna': dna}
    composed = composer.compose(dna)
    report['stages']['compose'] = {
        'files': {k: len(v.splitlines()) for k, v in composed['files'].items()},
        'stats': composed['stats'], 'manifest_entries': len(composed['manifest']),
        'fingerprint': composer.fingerprint(composed)}
    scan_composed = design_scan.scan_css('\n'.join(composed['files'].values()))
    report['stages']['verify_composed'] = scan_composed
    scan_before = design_scan.scan_css(css)
    applied = apply.apply_project(css, composed['files']['tokens.css'],
                                  composed['files']['motion.css'])
    scan_after = design_scan.scan_css(applied['css'])
    report['stages']['apply'] = {
        'changes': applied['changes'], 'removed_tells': applied['removed_tells'],
        'added_vars': applied['added_vars'],
        'before': {'clean': scan_before['clean_score'], 'tells': [t['id'] for t in scan_before['tells']]},
        'after': {'clean': scan_after['clean_score'], 'tells': [t['id'] for t in scan_after['tells']]},
        'lines': [len(css.splitlines()), len(applied['css'].splitlines())]}
    report['applied_css'] = applied['css']
    code_results = {}
    for name, src in code_files.items():
        code_results[name] = code_detector.analyze_code(src, name)
    avg_code = round(sum(r['total_score'] for r in code_results.values()) / max(1, len(code_results)), 3)
    report['stages']['code'] = {'files': {k: v['total_score'] for k, v in code_results.items()}, 'avg': avg_code}
    # 7b. DEEP TEXT scan (semantic layer)
    import text_deep
    deep_results = {}
    deep_fixed = {}
    for name, entries in content_collections.items():
        deep_results[name] = text_deep.analyze_collection_deep(entries)
        fixed_entries, changed = text_deep.targeted_contrast_reduction(entries)
        deep_fixed[name] = {
            'entries': fixed_entries, 'changed': len(changed),
            'after': text_deep.analyze_collection_deep(fixed_entries)['avg'],
            'before': deep_results[name]['avg']}
    report['stages']['deep_text'] = {
        'before': {k: v['avg'] for k, v in deep_results.items()},
        'after': {k: v['after'] for k, v in deep_fixed.items()},
        'changed': {k: v['changed'] for k, v in deep_fixed.items()}}
    report['deep_fixed_collections'] = {k: v['entries'] for k, v in deep_fixed.items()}

    content_results = {}
    for name, entries in content_collections.items():
        content_results[name] = corpus_detector.analyze_corpus(entries)['total_score']
    report['stages']['content'] = content_results
    # 9. COHERENCE — the capstone: does the project speak with one voice?
    import coherence
    content_for_coherence = '\n'.join(' '.join(e) if isinstance(e, list) else str(e)
                                       for e in content_collections.values())
    coh = coherence.analyze_coherence(content_for_coherence,
                                      '\n'.join(code_files.values()), css)
    report['stages']['coherence'] = coh

    report['summary'] = {
        'composed_clean': scan_composed['clean_score'],
        'applied_clean': scan_after['clean_score'],
        'code_avg': avg_code,
        'content_scores': content_results,
        'coherence': coh['total_score'],
        'coherence_verdict': coh['verdict'],
    }
    return report