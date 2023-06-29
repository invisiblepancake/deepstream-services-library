/*
The MIT License

Copyright (c) 2019-2023, Prominence AI, Inc.

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in-
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
*/

#ifndef _DSL_PROCESS_BINTR_H
#define _DSL_PROCESS_BINTR_H

#include "Dsl.h"
#include "DslApi.h"
#include "DslBintr.h"
#include "DslPadProbeHandler.h"
   
namespace DSL 
{
    /**
     * @brief convenience macros for shared pointer abstraction
     */
    #define DSL_MULTI_COMPONENTS_PTR std::shared_ptr<MultiComponentsBintr>

    #define DSL_MULTI_SINKS_PTR std::shared_ptr<MultiSinksBintr>
    #define DSL_MULTI_SINKS_NEW(name) \
        std::shared_ptr<MultiSinksBintr>(new MultiSinksBintr(name))

    #define DSL_DEMUXER_PTR std::shared_ptr<DemuxerBintr>
    #define DSL_DEMUXER_NEW(name, maxBranches) \
        std::shared_ptr<DemuxerBintr>(new DemuxerBintr(name, maxBranches))

    #define DSL_SPLITTER_PTR std::shared_ptr<SplitterBintr>
    #define DSL_SPLITTER_NEW(name) \
        std::shared_ptr<SplitterBintr>(new SplitterBintr(name))

    /**
     * @class MultiComponentsBintr
     * @brief Implements a base Tee binter that can add, link, unlink, and remove
     * child branches while in any state (NULL, PLAYING, etc.)
     */
    class MultiComponentsBintr : public Bintr
    {
    public: 
    
        /**
         * @brief ctor for the MultiComponentsBintr
         * @param[in] name name to give the new Bintr
         */
        MultiComponentsBintr(const char* name, const char* teeType);

        /**
         * @brief dtor for the MultiComponentsBintr
         */
        ~MultiComponentsBintr();

        /**
         * @brief adds a child ComponentBintr to this MultiComponentsBintr
         * @param[in] pChildComponent shared pointer to ComponentBintr to add
         * @return true if the ComponentBintr was added correctly, false otherwise
         */
        bool AddChild(DSL_BINTR_PTR pChildComponent);
        
        /**
         * @brief removes a child ComponentBintr from this MultiComponentsBintr
         * @param[in] pChildComponent a shared pointer to ComponentBintr to remove
         * @return true if the ComponentBintr was removed correctly, false otherwise
         */
        bool RemoveChild(DSL_BINTR_PTR pChildComponent);

        /**
         * @brief overrides the base method and checks in m_pChildComponents only.
         */
        bool IsChild(DSL_BINTR_PTR pChildComponent);

        /**
         * @brief overrides the base Noder method to only return the number of 
         * child ComponentBintrs and not the total number of children... 
         * i.e. exclude the nuber of child Elementrs from the count
         * @return the number of Child ComponentBintrs (branches) held by this 
         * MultiComponentsBintr
         */
        uint GetNumChildren()
        {
            LOG_FUNC();
            
            return m_pChildComponents.size();
        }

        /** 
         * @brief links all child Component Bintrs and their elements
         */ 
        bool LinkAll();
        
        /**
         * @brief unlinks all child Component Bintrs and their Elementrs
         */
        void UnlinkAll();
        
        /**
         * @brief sets the batch size for this Bintr
         * @param[in] batchSize the new batch size to use
         */
        bool SetBatchSize(uint batchSize);
        
    protected:
    
        DSL_ELEMENT_PTR m_pQueue;
        DSL_ELEMENT_PTR m_pTee;
        
        /**
         * @brief container of all child sources mapped by their unique names
         */
        std::map<std::string, DSL_BINTR_PTR> m_pChildComponents;

        /**
         * @brief Each source is assigned a unique stream id when linked
         * the vector is used on dynamic add/remove to find the next available
         * stream id.
         */
        std::vector<bool> m_usedStreamIds;
    
        /**
         * @brief adds a child Elementr to this PipelineSourcesBintr
         * @param pChildElement a shared pointer to the Elementr to add
         * @return a shared pointer to the Elementr if added correctly, 
         * nullptr otherwise
         */
        bool AddChild(DSL_BASE_PTR pChildElement);
        
        /**
         * @brief removes a child Elementr from this MultiComponentsBintr
         * @param pChildElement a shared pointer to the Elementr to remove
         */
        bool RemoveChild(DSL_BASE_PTR pChildElement);

    };

    /**
     * @class MultiSinksBintr
     * @brief Derived from the parent class MultiComponentsBintr, implements 
     * a Tee binter that can add, link, unlink, and remove child SinkBintrs 
     * while in any state (NULL, PLAYING, etc.)
     */
    class MultiSinksBintr : public MultiComponentsBintr
    {
    public: 
    
        /**
         * @brief ctor for the MultiSinksBintr
         * @param[in] name name to give the new Bintr
         */
        MultiSinksBintr(const char* name);

    };

    class SplitterBintr : public MultiComponentsBintr
    {
    public: 
    
        /**
         * @brief ctor for the MultiSinksBintr
         * @param[in] name name to give the new Bintr
         */
        SplitterBintr(const char* name);

        /**
         * @brief Adds the SplitterBintr to a Parent Pipeline/Branch Bintr
         * @param[in] pParentBintr Parent Pipeline/Branch to add this Bintr to
         */
        bool AddToParent(DSL_BASE_PTR pParentBintr);

    };

    class DemuxerBintr : public MultiComponentsBintr
    {
    public: 
    
        /**
         * @brief ctor for the DemuxerBintr
         * @param[in] name name to give the new Bintr
         */
        DemuxerBintr(const char* name, uint maxBranches);
        
        /**
         * @brief Adds the DemuxerBintr to a Parent Branch/Pipeline Bintr
         * @param[in] pParentBintr Parent Branch/Pipeline to add this Bintr to
         */
        bool AddToParent(DSL_BASE_PTR pParentBintr);

        /**
         * @brief Adds a child ComponentBintr to this DemuxerBintr. We need to 
         * override the parent class because we pre-allocate the requested pads.
         * This is a workaround for the NIVIDA demuxer limatation of not allowing
         * pads to be requested in a PLAYING state.
         * @param[in] pChildComponent shared pointer to ComponentBintr to add
         * @return true if the ComponentBintr was added correctly, false otherwise
         */
        bool AddChild(DSL_BINTR_PTR pChildComponent);
        
        /** 
         * @brief links all child Component Bintrs and their elements. We need to 
         * override the parent class because we pre-allocate the requested pads.
         * This is a workaround for the NIVIDA demuxer limatation of not allowing
         * pads to be requested in a PLAYING state.
         */ 
        bool LinkAll();

        /**
         * @brief unlinks all child Component Bintrs and their Elementrs.
         */
        void UnlinkAll();

    private:
    
        /**
         * @brief maximum number of branches this DemuxerBintr can connect.
         * Specifies the number of source pads to request prior to playing.
         */
        uint m_maxBranches;
    
        /**
         * @brief list of reguest pads -- maxBranches in length -- for the 
         * for the DemuxerBintr. The pads are preallocated on Bintr creation
         * and then used on LinkAll or AddChild when in a linked-state
         */
        std::vector<GstPad*> m_requestedSrcPads;
        
    };

}

#endif // _DSL_PROCESS_BINTR_H