from dbinteract import populate_db_by_event, add_sda_info, calculate_swisstour_pts, create_standings
import time

def main():
    # time the execution
    start_time = time.time()

    # define the event order and points for standings table
    event_order_and_pts = {#87177:100,  # Chili Open
                           #89585:200,  # Revolution
                           #90064:100,  # Spring Clang MPO/FPO
                           #90024:100,  # Spring Clang Other
                           ##:100,  # GPO
                           ##:100,  # Birdie Fest
                           ##:250,  # Meggen
                           ##:200,  # ZDGO
                           ##:100,  # Samnaun
                           ##:100,  # Lila's
                           ##:200,  # Eagle Open
                           ##:100,  # Lakeside
                           ##:250   # Bern Open
                           }  
    
    # populate the database with the results of the events
    # populate_db_by_event(87177)                   # Chili Open
    # populate_db_by_event(89585)                   # Revolution
    # populate_db_by_event(90064)                   # Spring Clang MPO/FPO
    # populate_db_by_event(90024)                   # Spring Clang Other
    # populate_db_by_event()                   # GPO
    # populate_db_by_event()                   # Birdie Fest
    # populate_db_by_event()                   # Meggen
    # populate_db_by_event()                   # ZDGO
    # populate_db_by_event()                   # Samnaun
    # populate_db_by_event()                   # Lila's
    # populate_db_by_event()                   # Eagle Open
    # populate_db_by_event()                   # Lakeside
    # populate_db_by_event()                   # Bern Open

    add_sda_info()

    calculate_swisstour_pts(event_order_and_pts)

    create_standings(event_order_and_pts)

    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"Elapsed time: {elapsed_time:.2f} seconds")

if __name__ == '__main__':
    main()