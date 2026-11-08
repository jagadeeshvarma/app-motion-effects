#!/usr/bin/env python3
"""Uniform GA01 regrading into a new directory; never rewrite first grades/results."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import sys
from run import run_process, base_environment, NATIVE_ENV

BASE = Path(__file__).resolve().parent


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--results',type=Path,required=True,help='Original private result root')
    parser.add_argument('--output',type=Path,required=True,help='New regrade directory, distinct from original root')
    parser.add_argument('--cases',default='ABCDEFGHIJKLMN')
    parser.add_argument('--native-grading-readiness',type=Path,help='Separate least-privilege generated-Dart grading proof')
    parser.add_argument('--safe-grading',action='store_true',default=True,help='Compatibility option: GA02 containment is always enabled')
    args=parser.parse_args()
    source=args.results.resolve();out=args.output.resolve()
    if out==source or out.is_relative_to(source):parser.error('Use a distinct regrade directory outside original results')
    out.mkdir(parents=True,exist_ok=True)
    wrapper=BASE/'graders/grade_with_trusted_inputs.py'
    wrapper_sha=hashlib.sha256(wrapper.read_bytes()).hexdigest()
    summary=[]
    for path in sorted(source.glob('*/result.json')):
        item=json.loads(path.read_text())
        if item.get('scenario') not in args.cases:continue
        if item.get('trigger_kind','positive')!='positive':continue
        ident=item.get('id',path.parent.name)
        target=out/(ident+'.json')
        if target.exists():raise SystemExit('Refusing to overwrite existing regrade: '+str(target))
        source_sha=hashlib.sha256(path.read_bytes()).hexdigest()
        argv=[sys.executable,str(wrapper),'--scenario',item['scenario'],'--workspace',item['workspace'],'--before-manifest',str(path),'--expected-manifest-sha256',source_sha]
        if args.safe_grading:argv+=['--safe-grading']
        if item['scenario'] in {'C','D'} and args.native_grading_readiness:argv+=['--native-grading-readiness',str(args.native_grading_readiness)]
        transcript=path.parent/'transcript.jsonl'
        if transcript.exists():argv+=['--transcript',str(transcript)]
        env=base_environment()
        environment_mode='host-legacy'
        native_env=Path(item['workspace']).parent/'runner-environment.json'
        if item['scenario'] in {'C','D'} and native_env.exists():
            values=json.loads(native_env.read_text())
            if set(values) not in (NATIVE_ENV,NATIVE_ENV-{'ANALYZER_STATE_LOCATION_OVERRIDE'},NATIVE_ENV-{'ANALYZER_STATE_LOCATION_OVERRIDE','ZDOTDIR'}):raise SystemExit('Recorded native environment has unexpected keys')
            env.update(values);environment_mode='recorded-public-native-zsh9' if set(values)==NATIVE_ENV else 'recorded-public-native-legacy-invalid-cohort'
        process=run_process(argv,timeout=180,env=env)
        try:grade=json.loads(process['stdout'])
        except json.JSONDecodeError:grade={'status':'blocked','reason':process['launch_error'] or 'Companion grader produced no JSON'}
        record={'id':ident,'scenario':item['scenario'],'condition':item['condition'],'trial':item['trial'],'source_result_sha256':source_sha,'source_first_grade_sha256':hashlib.sha256((path.parent/'grade.json').read_bytes()).hexdigest() if (path.parent/'grade.json').exists() else None,'companion_sha256':wrapper_sha,'safe_grading':args.safe_grading,'grading_environment':environment_mode,'grader_exit':process['returncode'],'grader':grade,'source_outputs_changed':False}
        with target.open('x') as stream:stream.write(json.dumps(record,indent=2)+'\n')
        row={key:record[key] for key in ['id','scenario','condition','trial','grader_exit']};row['status']=grade.get('status');summary.append(row);print(json.dumps(row),flush=True)
    summary_path=out/'summary.json'
    with summary_path.open('x') as stream:stream.write(json.dumps(summary,indent=2)+'\n')


if __name__=='__main__':main()
