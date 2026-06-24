from tools import *

print("Piese azi:", get_today_count())
print("Ultima piesa:", get_last_piece())
print("Fault azi:", get_fault_today())

print("\nStatus:")
print(get_machine_status())

print("\nUltimele loguri:")
print(get_recent_logs(10))
