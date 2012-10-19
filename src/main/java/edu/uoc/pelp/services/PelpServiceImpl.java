/*
	Copyright 2011-2012 Fundació per a la Universitat Oberta de Catalunya

	This file is part of PeLP (Programming eLearning Plaform).

    PeLP is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    PeLP is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
*/
package edu.uoc.pelp.services;

import edu.uoc.pelp.bussines.UOC.UOCPelpBussines;
import edu.uoc.pelp.bussines.UOC.exception.InvalidSessionException;
import edu.uoc.pelp.bussines.vo.Subject;
import java.util.logging.Level;
import java.util.logging.Logger;

/**
 * Services implementation class
 * @author Xavier Baró
 */
public class PelpServiceImpl implements PelpService {
    
    private UOCPelpBussines bussines;
    
    /**
     * Default constructor
     */
    public PelpServiceImpl(UOCPelpBussines bussines) {
        super();
        this.bussines=bussines;
    }

    @Override
    public Subject[] getUserSujects(String campusSession) {
        Subject[] ret=new Subject[2];
        if(bussines!=null) {
            try {
                bussines.setCampusSession(campusSession);
            } catch (InvalidSessionException ex) {
                Logger.getLogger(PelpServiceImpl.class.getName()).log(Level.SEVERE, null, ex);
            }
            ret[0]=new Subject("Semester1__BussinesOK_");
        } else {
            ret[0]=new Subject("Semester1__NullBussines");
        }
        if(campusSession!=null) {
            ret[1]=new Subject("Semester2__" + campusSession);
        } else {
            ret[1]=new Subject("Semester2__NullCampusSession");
        }
        return ret;
    }
    
    /**
     * Get the active subjects for current user
     * @param campusSession Campus session
     * @return List of subjects
     */
   /* @Override
    public UOCSubject[] getUserSujects(String campusSession) {
        UOCSubject[] retObject=new UOCSubject[3];
        retObject[0]=new UOCSubject("20121","05.123");
        retObject[1]=new UOCSubject("20121","05.456");
        retObject[2]=new UOCSubject("20121","05.789");
        
        return retObject;
    }
    
    /**
     * Add a new deliver of current user for given activity
     * @param campusSession Campus session
     * @param activity Activity object
     * @param files Files to be delivered
     * @return Result for new added deliver.
     */
   /* @Override
    public DeliverDetail addDeliver(String campusSession,Activity activity, DeliverFile[] files) {
        return null;
    }
    
    /**
     * Get all the delivers of current user for given activity
     * @param campusSession Campus session
     * @param activity Activity object
     * @return List of results.
     */
 /*   @Override
    public DeliverDetail[] getDelivers(String campusSession,Activity activity) {
        return null;
    }*/
/*
    public UOCPelpBussines getBussines() {
        return bussines;
    }

    public void setBussines(UOCPelpBussines bussines) {
        this.bussines = bussines;
    }
    */
    
}
