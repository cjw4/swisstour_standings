from dbinteract import populate_db_by_event, add_sda_info, calculate_swisstour_pts, create_standings
import time

def main():
    # time the execution
    start_time = time.time()

    # define the event order and points for standings table
    event_order_and_pts = {87177:[100,"Chili Open"],  # Chili Open
                           89585:[200, "Revolution"],  # Revolution
                           #90064:[100, "Spring Clang]",  # Spring Clang MPO/FPO
                           #90024:[100, "Spring Clang]"  # Spring Clang Other
                           #91659:[100, "GPO]",  # GPO
                           #91840:[100, "Birde Fest"],  # Birdie Fest
                           #92323:[200, "ZDGO"],  # ZDGO
                           #92343:[250, "Meggen (Swiss Championships)",  # Meggen
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
    # populate_db_by_event(91659)                   # GPO
    # populate_db_by_event(91840)                   # Birdie Fest
    # populate_db_by_event(92323)                   # ZDGO
    # populate_db_by_event(92343)                   # Meggen
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