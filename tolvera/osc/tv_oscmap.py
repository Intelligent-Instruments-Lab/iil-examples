from tolvera import Tolvera, run

def main(**kwargs):
    tv = Tolvera(**kwargs)

    '''
    Patcher → Python
    '''
    update_rate = 5

    @tv.osc.map.receive_args(arg=(0,0,100), count=update_rate)
    def test_receive_args(arg: float):
        print(f"Receiving args: {arg}")

    @tv.osc.map.receive_list(vector=(0.0,0.0,100.0), length=10, count=update_rate)
    def test_receive_list(vector: list[float]):
        print(f"Receiving list: {vector}")

    '''
    Python → Patcher
    '''
    update_rate = 7
    send_mode = 'broadcast' # | 'event'

    @tv.osc.map.send_args(arg=(0,0,100), count=update_rate, send_mode=send_mode)
    def test_send_arg() -> list[int]:
        arg = 5
        print(f"Sending arg: {arg}")
        return [arg]
    
    @tv.osc.map.send_list(vector=(0.,0.,100.), length=10, count=update_rate, send_mode=send_mode)
    def test_send_list() -> list[float]:
        print(f"Sending list: {[0]*10}")
        return [0]*10

    @tv.render
    def _():
        tv.px.diffuse(0.99)
        tv.v.flock(tv.p)
        tv.px.particles(tv.p, tv.s.species())
        return tv.px

if __name__ == '__main__':
    run(main)
