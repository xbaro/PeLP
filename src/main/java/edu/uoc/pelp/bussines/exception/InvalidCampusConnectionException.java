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
package edu.uoc.pelp.bussines.exception;

import edu.uoc.pelp.exception.PelpException;

/**
 * Invalid campus connection exception class for PeLP. Launched when detected some 
 * error in the campus connection.
 * @author Xavier Baró
 */
public class InvalidCampusConnectionException extends PelpException {
    public InvalidCampusConnectionException(String msg) {
        super(msg);
    }

    public InvalidCampusConnectionException() {
        super("Invalid CampusConnection exception.");
    }  
}
