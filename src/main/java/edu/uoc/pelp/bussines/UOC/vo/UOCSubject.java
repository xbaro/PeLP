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
package edu.uoc.pelp.bussines.UOC.vo;

import edu.uoc.pelp.bussines.vo.*;

/**
 * Subject information
 * @author Xavier Baró
 */
public class UOCSubject extends Subject {
    // Semester 
    private String _semester;
    private String _subjectCode;
    
    public UOCSubject() {
        super();
    }
    
    public UOCSubject(String semester, String subject) {
        super();
        this._semester=semester;
        this._subjectCode=subject;
    }
    
    public String getSemester() {
        return _semester;
    }

    public void setSemester(String _semester) {
        this._semester = _semester;
    }

    public String getSubjectCode() {
        return _subjectCode;
    }

    public void setSubjectCode(String subjectCode) {
        this._subjectCode = subjectCode;
    }
}