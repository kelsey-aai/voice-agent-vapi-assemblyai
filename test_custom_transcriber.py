"""Integration test: fake Vapi client -> custom_transcriber -> mock AssemblyAI server. Run: python test_custom_transcriber.py"""
import asyncio, json, os, sys, threading, time, array
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); os.environ['ASSEMBLYAI_API_KEY'] = 'test-key'
import websockets, uvicorn
import custom_transcriber as ct

received = {}
async def mock_aai(ws):
    received['path'] = ws.request.path; received['auth'] = ws.request.headers.get('Authorization')
    got = b''
    async for m in ws:
        if isinstance(m, bytes):
            got += m
            if len(got) >= 6:
                await ws.send(json.dumps({"type": "Turn", "end_of_turn": False, "transcript": "my number"}))
                await ws.send(json.dumps({"type": "Turn", "end_of_turn": True, "transcript": "My number is 555-0134."}))
        else:
            received['text'] = m; break
    received['audio'] = got

async def main():
    srv = await websockets.serve(mock_aai, '127.0.0.1', 8765)
    ct.AAI_WS_BASE = 'ws://127.0.0.1:8765/v3/ws'
    config = uvicorn.Config(ct.app, host='127.0.0.1', port=8766, log_level='warning')
    server = uvicorn.Server(config); task = asyncio.create_task(server.serve())
    await asyncio.sleep(1)
    out = []
    async with websockets.connect('ws://127.0.0.1:8766/api/custom-transcriber') as v:
        await v.send(json.dumps({"type": "start", "encoding": "linear16", "container": "raw", "sampleRate": 16000, "channels": 2}))
        await v.send(array.array('h', [1, 100, 2, 200, 3, 300]).tobytes())
        out.append(json.loads(await v.recv())); out.append(json.loads(await v.recv()))
    await asyncio.sleep(0.5)
    server.should_exit = True; await task; srv.close()
    print(out); print(received)
    assert out[0]['transcriptType'] == 'partial' and out[1]['transcriptType'] == 'final'
    assert received['audio'] == array.array('h', [1, 2, 3]).tobytes()
    assert received['auth'] == 'test-key' and 'assemblyai-stt-3-7-realtime-agent' in received['path']
    print('PASS')
asyncio.run(main())
