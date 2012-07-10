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
package edu.uoc.pelp.engine.aem;

import edu.uoc.pelp.exception.AuthPelpException;
import edu.uoc.pelp.exception.ExecPelpException;
import java.io.File;
import java.io.IOException;
import java.util.ArrayList;

/**
 * This class represent a programming project consisting of several code files.
 * @author Xavier Baró
 */
public class CodeProject {
    /**
     * Path where files are stored
     */
    private File _path=null;
    
    /**
     * Main file of the project. Relative to the project path.
     */
    private File _mainFile=null;
    
    /**
     * All the files of the project, relative to the project path. Main file must be in this list.
     */
    private ArrayList<File> _srcFiles=null;
    
    /**
     * Default constructor. 
     * @param rootPath Path where files are stored.
     */
    public CodeProject(File rootPath) {
        _path=rootPath;
    }
    
    /**
     * Add a new file to the project. Files are assumed to be relative to rootPath, if not,
     * the rootPath is removed from the given path.
     * @param newFile File to add. The file must exists and be inside the rootPath.
     * @throws ExecPelpException If the file does not exist or is outside the rootPath
     */
    public void addFile(File newFile) throws ExecPelpException {
        
        // Check the new file (path and existence)
        checkFile(newFile);
        
        // Get relative path to the root path
        newFile=getRelativePath(newFile);
        
        // Create the arraylist
        if(_srcFiles==null) {
            _srcFiles=new ArrayList<File>();
        }
        
        // Check that the file is not in the list
        boolean found=false;
        for(File f:_srcFiles) {
            if(f.equals(newFile)) {
                found=true;
                break;
            }
        }
        
        // If the file is not in the list, add it
        if(!found) {
            _srcFiles.add(newFile);
        }
    }
    
    /**
     * Add a new main file to the project. File is assumed to be relative to rootPath, if not,
     * the rootPath is removed from its path. If it does not exist the list of files, it is also 
     * added to the list of files.
     * @param newFile File to add. The file must exists and be inside the rootPath.
     * @throws ExecPelpException If the file does not exist or is outside the rootPath
     */
    public void addMainFile(File newFile) throws ExecPelpException{
        // Check the new file (path and existence)
        checkFile(newFile);
        
        // Get relative path to the root path
        newFile=getRelativePath(newFile);
        
        // Store as main file
        _mainFile=newFile;
        
        // Add to the list of files
        addFile(newFile);
    }
    
    /**
     * Move the project files to the given path, and use new location.
     * @param dstPath Final path where files are moved.
     * @throws AuthPelpException Not enought rights to perform file operation
     */
    public void moveFiles(File dstPath) throws AuthPelpException, ExecPelpException {
        
        // Check that files can be readed
        for(File f:getAbsoluteFiles()) {
            if(!f.canRead()) {
                throw new AuthPelpException("Cannot read file " + f.getAbsolutePath());
            }
        }
        
        // Check permisions for output directory
        if(!dstPath.exists()) {
            // Create the output directory
            if(!dstPath.mkdirs()) {
                throw new AuthPelpException("Cannot create output directory: " + dstPath.getAbsolutePath());
            }
        } else if(!dstPath.isDirectory()){
            throw new ExecPelpException("Cannot move to a file. Output path must be a directory.");
        }
        
        // Move all files to the destination directory        
        for(File f:getRelativeFiles()) {
            File src=null;
            File dst=null;
            try {
                src=new File(_path.getCanonicalPath()+File.separator+f.getPath());
                dst=new File(dstPath.getCanonicalPath()+File.separator+f.getPath());
                if(!src.renameTo(dst)) {
                    throw new ExecPelpException("Cannot move file \"" + src.getAbsolutePath() + "\" to \"" + dst.getAbsolutePath() + "\"");
                }
            } catch (IOException ex) {
                throw new ExecPelpException("Cannot move file \"" + src.getAbsolutePath() + "\" to \"" + dst.getAbsolutePath() + "\"");
            }
        }   
        
        // Once moved, change the root path
        _path=dstPath;
    }     
    
    /**
     * Gets the list of files in the current project.
     * @return List with the relative path of each file in the project
     */
    public File[] getRelativeFiles() {
        File[] retArray=null;
        if(_srcFiles!=null) {
            retArray=new File[_srcFiles.size()];
            _srcFiles.toArray(retArray);
        } else {
            retArray=new File[0];
        }
                
        return retArray;
    }
    
    /**
     * Gets the list of files in the current project.
     * @return List with the absolute path of each file in the project
     */
    public File[] getAbsoluteFiles() {                
        File[] retArray=getRelativeFiles();
        for(int i=0;i<retArray.length;i++) {
            retArray[i]=getAbsolutePath(retArray[i],null);
        }
        return retArray;
    }
    
    /**
     * Returns the absolut path of a given relative/absolute path from a certain root path.
     * @param file Relative or Absolute file.
     * @param rootPath Root path. If null, default root path is used.
     * @return Absolute file object.
     */
    public File getAbsolutePath(File file,File rootPath) {
        File absFile=null;
        
        // If no rootPath is provided, use default
        if(rootPath==null) {
            rootPath=_path;
        }
        
        // Be sure that this file is in relative form
        File relFile=getRelativePath(file);
        
        // Add the root path to the file
        if(relFile!=null) {
            absFile=new File(rootPath.getAbsolutePath()+File.separator+relFile.getPath());
        } else {
            String strPath=file.getPath();
            if(strPath.length()>0 && strPath.charAt(0)==File.separatorChar) {
                strPath.substring(1);
            }
            absFile=new File(rootPath.getAbsolutePath()+File.separator+strPath);
        }
        
        return absFile;
    }

    /**
     * Returns the relative path of a given relative/absolute path from a certain root path.
     * @param file Relative or Absolute file.
     * @param rootPath Root path. If null, default root path is used.
     * @return Absolute file object.
     */
    public File getRelativePath(File file) {
        File relFile=null;
        
        try {
            // Get canonical paths
            String absFilePath=file.getCanonicalPath();
            String absRootPath=_path.getCanonicalPath();
            
            // Find root path in file path
            if(absFilePath.contains(absRootPath)) {
                String strPath=absFilePath.substring(absRootPath.length());
                if(strPath.charAt(0)==File.separatorChar) {
                    strPath=strPath.substring(1);
                }
                if(strPath.length()>0) {
                    relFile=new File(strPath);
                }
            } else {
                // Assume it as relative
                String strPath=file.getPath();
                if(strPath.length()>0 && strPath.charAt(0)==File.separatorChar) {
                    strPath.substring(1);
                }
                relFile=new File(strPath);                
            }
        } catch (IOException ex) {
            return null;
        }
        
        return relFile;
    }
    
    /**
     * Gets the main file
     * @return Main file
     */
    public File getMainFile() {
        return _mainFile;
    }

    /**
     * Ckech that a given file exist and is inside the root path
     * @param newFile File to be checked
     * @throws ExecPelpException If the file does not exist or is out of the root path.
     */
    private void checkFile(File newFile) throws ExecPelpException {
        // Get relative path to the root path
        newFile=getRelativePath(newFile);
        
        // Check that given file is in the root path.
        if(newFile==null) {
            throw new ExecPelpException("New file is not in the root path.");
        }
        
        // Check that given file exists
        if(!getAbsolutePath(newFile,null).exists()) {
            throw new ExecPelpException("File not found: \"" + getAbsolutePath(newFile,null).getAbsolutePath() + "\"");
        }
    }
}
